import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.Chunker import node_chunk, feeder_summary_chunk
from utils.VectorStore import VectorStore
import json


FEEDER_ID = "304W5"

current_file_parent = Path(__file__).resolve().parent
log_dir = current_file_parent.parent / "logs"

store = VectorStore(FEEDER_ID)

ids       = []
texts     = []
metadatas = []

# -- Feeder summary --
summary_path = log_dir / f"{FEEDER_ID}-FeederSummary.json"
with open(summary_path, "r") as f:
    feeder_stats = json.load(f)

ids.append(f"{FEEDER_ID}_feeder_summary")
texts.append(feeder_summary_chunk(feeder_stats))
metadatas.append({
    "doc_type":  "feeder_summary",
    "feeder_id": feeder_stats["feeder_id"],
    "op_dist":   feeder_stats["op_dist"],
})

# -- Node summaries --
node_path = log_dir / f"{FEEDER_ID}-Nodesummary.jsonl"
with open(node_path, "r") as f:
    for line in f:
        item = json.loads(line)

        ids.append(item["node_id"])
        texts.append(node_chunk(item))
        metadatas.append({
            "doc_type"        : "node",
            "node_id"         : item["node_id"],
            "feeder_id"       : item["feeder_id"],
            "sub_id"          : item["sub_id"],
            "vlevel"          : item["vlevel"],
            "con_type"        : item["con_type"],
            "energized"       : item["energized"],
            "depth"           : item["depth"] if item["depth"] is not None else -1,
            "decision_reason" : item["decision_reason"] or "",
            "blocking_device" : item["blocking_device"] or "",
            "load_count"      : len(item["loads"]),
            "capacitor_count" : len(item["capacitors"]),
            "site_count"      : len(item["sites"]),
            "mpoint_count"    : len(item["mpoints"]),
        })

store.upsert_batch(ids=ids, documents=texts, metadatas=metadatas)
print(f"Indexed {len(ids)} documents into collection '{FEEDER_ID}' (1 feeder summary + {len(ids)-1} nodes)")
