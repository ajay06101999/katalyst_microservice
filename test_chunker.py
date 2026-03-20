# json_test_data = {"node_id": "382576406", "vlevel": "10", "con_type": "1", "sub_id": "379156530", "energized": false, "parent": "382576392", "depth": 147, "phase": null, "loads": [{"load_id": "NE_OH_382576406", "no_key": "382576406", "phase": "010", "load_type": "0", "status": "010", "descriptive_loc": "pole# 35 SOUTH OXFORD RD MILLBURY", "sub_area": "1121", "state": "1"}], "capacitors": [], "sites": [], "mpoints": [], "decision_reason": "parent_de_energized_propagated", "blocking_device": null, "trace_id": "62bd3bfd-6417-4185-b8d9-d82311ed6fa7", "feeder_id": "304W5", "source_type": "python"}
from pathlib import Path
import json
from utils.NodeChunker import chunk


current_file_parent = Path(__file__).resolve().parent
print(current_file_parent)
json_path = current_file_parent /"logs/304W5-Nodesummary.jsonl"


def run_chunker():
     with open(json_path, 'r') as f:
          for i,line in enumerate(f):
               record = json.loads(line)
               if len(record["mpoints"]) > 0:
                    print(record)
                    print(chunk(record))
                    
                    break
          

