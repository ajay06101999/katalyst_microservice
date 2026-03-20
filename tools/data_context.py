from pathlib import Path
import json
from utils.VectorStore import VectorStore


class DataContext:
    def __init__(self, feeder_id, feeder_summary, node_map, parent_map, blocking_device_map, vector_store):
        self.feeder_id            = feeder_id
        self.feeder_summary       = feeder_summary
        self.node_map             = node_map          
        self.parent_map           = parent_map        
        self.de_energized_section_head_map  = de_energized_section_head_map 
        self.vector_store         = vector_store
    
    @classmethod
    def load(cls, feeder_id: str) -> "DataContext":
        base = Path(__file__).resolve().parent.parent
        log_dir = base / "logs"
        
        with open(log_dir / f"{feeder_id}-FeederSummary.json") as f:
            feeder_summary = json.load(f)
        
        node_map, parent_map, de_energized_section_head_map = {}, {}, {}
        with open(log_dir / f"{feeder_id}-Nodesummary.jsonl") as f:
            for line in f:
                doc = json.loads(line)
                nid = doc["node_id"]
                node_map[nid] = doc
                if doc.get("parent"):
                    parent_map[nid] = doc["parent"]
                if doc.get("blocking_device"):
                    de_energized_section_head_map[nid] = doc["blocking_device"]

        vector_store = VectorStore(feeder_id)

        return cls(feeder_id, feeder_summary, node_map, parent_map, de_energized_section_head_map, vector_store)

       

