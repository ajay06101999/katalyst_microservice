from collections import defaultdict, Counter
from Entities.DataModel import Vertex , Edge , Device , Capacitor , Mpoint , Load , Site
from utils.TraceLogger import TraceLogger
from pathlib import Path
import logging
import json
from dataclasses import asdict

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


class Graph:
    def __init__(self , extracts , feeder_id , op_dist , source_type):
        self.feeder_id = feeder_id
        self.op_dist = op_dist
        self.source_type = source_type
        self.extract = extracts

        self.vertex_dict = {}
        self.edge_dict = {}
        self.device_dict = {}

        self.root = None
        self.adj_dict = defaultdict(list)
        self.visited = set()
        self.nodes_with_open_devices = []
        self.total_device_placement = 0

        self.enrichedLoad = 0
        self.enrichedCapacitor = 0
        self.enrichedSite = 0
        self.enrichedMpoint = 0


        
        self.build_graph()


    def build_trace_assets(self):
        for _ , row in self.extract["node_data"].iterrows():
            self.vertex_dict[row["NID"]] = Vertex.from_row(row)

        for _ , row in self.extract["line_data"].iterrows():
            self.edge_dict[row["ID"]] = Edge.from_row(row)


        for _ , row in self.extract["device_data"].iterrows():
            did = row["DID"]
            if did in self.device_dict:
                continue
            created_device = Device.from_row(row)
            self.device_dict[did] = created_device
            if row["LI_KEY"] in self.edge_dict:
                self.total_device_placement+=1
                self.edge_dict[row["LI_KEY"]].devices.append(created_device)
            else:
                logging.warning("Device %s references unknown line %s", row["DID"], row["LI_KEY"])

        for edge in self.edge_dict.values():
            self.adj_dict[edge.no_key1].append((edge.no_key2, edge))
            self.adj_dict[edge.no_key2].append((edge.no_key1, edge))

    

    def initializeTrace(self):
        swing_source = self.extract["source_data"].query("STYPE == '1'")
        if len(swing_source) == 0:
            raise ValueError("No Swing Source found!")
        if len(swing_source) > 1:
            logging.warning("More than one Swing Source found!")
        
        
        self.root = swing_source["NO_KEY"].iloc[0]
        if self.root not in self.vertex_dict:
            raise KeyError(f"Root Node Id : {self.root} not found in VertexDict")

        root_vertex = self.vertex_dict[self.root]
        root_vertex.energized = True
        root_vertex.depth = 0
        root_vertex.decision_reason = "swing_source"
        logging.info("Swing source found — root node %s initialised", self.root)
        self.logger.emit("LIFECYCLE","ROOT_INITIALIZED" , vertex_id = self.root , depth=0)

    def buildTopology(self):
        stack = [self.root]
        self.visited.add(self.root)
        boundary_skipped = 0
        self.logger.emit("LIFECYCLE", "DFS_STARTED", root = self.root)

        while stack:
            node = stack.pop()
            current_vertex = self.vertex_dict[node]
     
            for neighbor_id, edge in self.adj_dict[node]:
                if neighbor_id in self.visited:
                    continue
                self.visited.add(neighbor_id)
                neighbor_vertex = self.vertex_dict.get(neighbor_id)
                if neighbor_vertex is None:
                    boundary_skipped+=1
                    logging.warning("Node %s in adj but not in vertex_dict — boundary node, skipping", neighbor_id)
                    self.logger.emit("TRAVERSAL" , "BOUNDARY_NODE_SKIPPED" , vertex_id = neighbor_id , from_node = node)
                    continue
                next_depth = current_vertex.depth + 1
                if edge.is_blocked or not current_vertex.energized:
                    neighbor_vertex.energized = False
                    
                    if edge.is_blocked:
                        neighbor_vertex.decision_reason = "edge_blocked_by_open_device"
                        blocking_device = next((d.device_id for d in edge.devices if d.is_open), None)
                        neighbor_vertex.blocking_device =  blocking_device
                        self.nodes_with_open_devices.append(neighbor_id)
                        self.logger.emit("DECISION", "NODE_DE_ENERGIZED",
                                        vertex_id = neighbor_id,
                                        parent_node = node,
                                        incoming_edge_id = edge.line_id,
                                        depth = next_depth,
                                        decision_reason = "edge_blocked_by_open_device",
                                        blocking_device = blocking_device)
                         
                    else:
                        neighbor_vertex.decision_reason = "parent_de_energized_propagated"
                        self.logger.emit("DECISION", "NODE_DE_ENERGIZED" ,
                                         vertex_id = neighbor_id,
                                         parent_node = node,
                                         depth = next_depth,
                                         incoming_edge_id = edge.line_id,
                                         decision_reason = "parent_de_energized_propagated",
                                         blocking_device = None)

                else:
                    neighbor_vertex.energized = True
                    neighbor_vertex.decision_reason = "parent_energized_no_blocking_device"
                    self.logger.emit("DECISION", "NODE_ENERGIZED", 
                                     vertex_id = neighbor_id,
                                     parent_node = node ,
                                     depth = next_depth,
                                     incoming_edge_id = edge.line_id,
                                     decision_reason = "parent_energized_no_blocking_device",
                                     blocking_device = None
                                     )
                neighbor_vertex.parent = node
                neighbor_vertex.depth = next_depth
                neighbor_vertex.phase = edge.phase_perm
                stack.append(neighbor_id)
        self.logger.emit("LIFECYCLE", "DFS_COMPLETE" ,
                        visited_vertex_count = len(self.visited),
                        de_energized_count = len(self.nodes_with_open_devices),
                        boundary_skipped = boundary_skipped)
        


    def enrichAttributes(self):
        self.logger.emit("LIFECYCLE", "ENRICHMENT_START")

        for _, row in self.extract["load_data"].iterrows():
            vertex = self.vertex_dict.get(row["NO_KEY"])
            if vertex is None:
                logging.warning("Load %s references unknown node %s", row["LOID"], row["NO_KEY"])
                continue
            vertex.loads.append(Load.from_row(row))
            self.enrichedLoad += 1
            self.logger.emit("ENRICHMENT" , "LOAD_ENRICHMENT",
                             load_id = row["LOID"],
                             vertex_id = row["NO_KEY"])

        for _, row in self.extract["capacitor_data"].iterrows():
            vertex = self.vertex_dict.get(row["NO_KEY"])
            if vertex is None:
                logging.warning("Capacitor %s references unknown node %s", row["CAID"], row["NO_KEY"])
                continue
            vertex.capacitors.append(Capacitor.from_row(row))
            self.enrichedCapacitor += 1
            self.logger.emit("ENRICHMENT" , "CAPACITOR_ENRICHMENT",
                             capacitor_id = row["CAID"],
                             vertex_id = row["NO_KEY"])

        for _, row in self.extract["site_data"].iterrows():
            vertex = self.vertex_dict.get(row["NO_KEY"])
            if vertex is None:
                logging.warning("Site %s references unknown node %s", row["SIID"], row["NO_KEY"])
                continue
            vertex.sites.append(Site.from_row(row))
            self.enrichedSite += 1
            self.logger.emit("ENRICHMENT" , "SITE_ENRICHMENT",
                             site_id = row["SIID"],
                             vertex_id = row["NO_KEY"])

        for _, row in self.extract["mpoint_data"].iterrows():
            vertex = self.vertex_dict.get(row["NO_KEY"])
            if vertex is None:
                logging.warning("Mpoint %s references unknown node %s", row["MPID"], row["NO_KEY"])
                continue
            vertex.mpoints.append(Mpoint.from_row(row))
            self.enrichedMpoint += 1
            self.logger.emit("ENRICHMENT" , "MPOINT_ENRICHMENT", 
                             mpoint_id = row["MPID"],
                             vertex_id = row["NO_KEY"])
        
        self.logger.emit("LIFECYCLE", "ENRICHMENT_COMPLETE", 
                         total_enriched_load = self.enrichedLoad,
                         total_enriched_capacitor = self.enrichedCapacitor,
                         total_enriched_site = self.enrichedSite,
                         total_enriched_mpoint = self.enrichedMpoint)
        
    
    def generateFeederSummary(self):
        # -- Feeder / substation metadata --
        feeder_row    = self.extract["feeder_data"].iloc[0]
        feeder_name   = feeder_row["NAME"]
        feeder_sub_id = feeder_row["SUB_ID"]

        sub_df   = self.extract["substation_data"]
        sub_row  = sub_df[sub_df["SUB_ID"] == feeder_sub_id]
        sub_name = sub_row["NAME"].iloc[0]     if len(sub_row) else "Unknown"
        district = sub_row["DISTRICT"].iloc[0] if len(sub_row) else "Unknown"

        # -- Topology --
        total_nodes   = len(self.vertex_dict)
        total_edges   = len(self.edge_dict)
        total_devices = len(self.device_dict)

        depths    = [v.depth for v in self.vertex_dict.values() if v.depth is not None]
        max_depth = max(depths) if depths else 0

        # -- Energization --
        energized_nodes    = sum(1 for v in self.vertex_dict.values() if v.energized)
        de_energized_nodes = total_nodes - energized_nodes
        directly_blocked   = sum(1 for v in self.vertex_dict.values()
                                 if v.decision_reason == "edge_blocked_by_open_device")
        propagated         = sum(1 for v in self.vertex_dict.values()
                                 if v.decision_reason == "parent_de_energized_propagated")

        # -- Devices --
        open_devices   = [d for d in self.device_dict.values() if d.is_open]
        closed_devices = [d for d in self.device_dict.values() if not d.is_open]
        devcat_counts  = Counter(d.dev_cat  for d in self.device_dict.values())
        devtype_counts = Counter(d.dev_type for d in self.device_dict.values())

        stats = {
            "feeder_id":           self.feeder_id,
            "feeder_name":         feeder_name,
            "op_dist":             self.op_dist,
            "sub_id":              feeder_sub_id,
            "sub_name":            sub_name,
            "district":            district,
            "trace_id":            self.logger.trace_id,
            "root_node":           self.root,
            "total_nodes":         total_nodes,
            "total_edges":         total_edges,
            "total_devices":       total_devices,
            "max_depth":           max_depth,
            "energized_nodes":     energized_nodes,
            "de_energized_nodes":  de_energized_nodes,
            "directly_blocked":    directly_blocked,
            "propagated":          propagated,
            "open_device_count":   len(open_devices),
            "closed_device_count": len(closed_devices),
            "open_devices":        [
                {"device_id": d.device_id, "dev_cat": d.dev_cat, "dev_type": d.dev_type, "line_id": d.line_id}
                for d in open_devices
            ],
            "devcat_counts":       dict(devcat_counts),
            "devtype_counts":      dict(devtype_counts),
            "total_loads":         self.enrichedLoad,
            "total_capacitors":    self.enrichedCapacitor,
            "total_sites":         self.enrichedSite,
            "total_mpoints":       self.enrichedMpoint,
        }

        current_dir = Path(__file__).resolve().parent
        log_folder  = current_dir / "logs"
        log_folder.mkdir(exist_ok=True)
        json_path = log_folder / f"{self.feeder_id}-FeederSummary.json"

        with open(json_path, "w") as f:
            json.dump(stats, f, indent=2)

        self.logger.emit("LIFECYCLE", "FEEDER_SUMMARY_GENERATED",
                         energized_nodes=energized_nodes,
                         de_energized_nodes=de_energized_nodes,
                         open_device_count=len(open_devices))

        return stats

    def generateNodeSummaries(self):
        current_dir = Path(__file__).resolve().parent
        log_folder = current_dir / "logs"
        log_folder.mkdir(exist_ok = True)
        file_path = log_folder / f"{self.feeder_id}-Nodesummary.jsonl"
        with open(file_path , "w") as f:
            for vertex in self.vertex_dict.values():
                doc = asdict(vertex)
                doc["trace_id"] = self.logger.trace_id
                doc["feeder_id"] = self.feeder_id
                doc["source_type"] = self.source_type
                f.write(json.dumps(doc) + "\n")

    def build_graph(self):
        
        try:
            self.build_trace_assets()
            self.logger = TraceLogger(self.feeder_id ,self.source_type, len(self.vertex_dict) , len(self.edge_dict))
            self.initializeTrace()
            self.buildTopology()
            self.enrichAttributes()
            self.generateFeederSummary()
            self.generateNodeSummaries()
        finally:
            if hasattr(self, "logger"):
                self.logger.close()

        
        