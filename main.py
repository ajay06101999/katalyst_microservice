import os
import logging

import pandas as pd
from pathlib import Path
from graph import Graph
from utils.constants import FILE_NAMES 
from utils.helpers import check_headers


logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

file_path = Path(__file__).resolve()
script_dir = file_path.parent

os.chdir(script_dir)

EXTRACT_DIR = "./Extracts/"
OP_DIST     = "01"
FEEDER_ID   = "304W5"

extract_data = {}

for file_name in FILE_NAMES:
    file_path = os.path.join(EXTRACT_DIR, f"{file_name}_{OP_DIST}_{FEEDER_ID}.csv")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Missing extract file: {file_path}")

    df = pd.read_csv(
        file_path,
        dtype=str,           # all columns read as str — prevents ID precision loss
        keep_default_na=False,  # empty cells → "" not NaN
    )

    df.columns = df.columns.str.strip()          # strip whitespace from column names
    df= df.apply(lambda c: c.str.strip()) # strip whitespace from all values

    if not check_headers(file_name, df.columns.tolist()):
        logging.warning(f"Missing or invalid columns in {file_name}")

    extract_data[f"{file_name.lower()}_data"] = df

G1 = Graph(extract_data , FEEDER_ID , OP_DIST , "python" )
print(f"Total count of edge_dict : {len(G1.edge_dict)}")
print(f"Total count of device_dict : {len(G1.device_dict)}")
print(f"Total count of vertex_dict : {len(G1.vertex_dict)}")
            