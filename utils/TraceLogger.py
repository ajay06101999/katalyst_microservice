import uuid
import json
from .helpers import getTimestamp
from pathlib import Path



class TraceLogger:
    def __init__(self, feeder_id , source_type , node_count , edge_count):
        self.trace_id = str(uuid.uuid4())
      
        self.feeder_id = feeder_id
        self.source_type = source_type

        current_dir = Path(__file__).resolve().parent
        parent_dir = current_dir.parent
        log_folder = parent_dir / "logs"
        log_folder.mkdir(exist_ok=True)
        self.file_path = log_folder /f"{self.feeder_id}-{self.source_type}.jsonl"
        
        initial_payload = {
            "node_count" : node_count, 
            "edge_count" : edge_count
        }
        self._file = open( self.file_path , "a")
        self.emit("LIFECYCLE" , "TRACE_STARTED" , **initial_payload)


        
    
    def emit(self , event_type , event_subtype , **payload ):
        record = {
            "trace_id" : self.trace_id,
            "feeder_id" : self.feeder_id,
            "source_type" : self.source_type,
            "timestamp" : getTimestamp(),
            "event_type": event_type,
            "event_subtype": event_subtype
        }
        record.update(payload)
        self._file.write(json.dumps(record) + "\n")
        self._file.flush()

    def close(self):
        self.emit("LIFECYCLE", "TRACE_COMPLETE")
        self._file.close()