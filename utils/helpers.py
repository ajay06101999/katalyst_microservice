from datetime import datetime, timezone
import logging
from utils.constants import EXPECTED_HEADERS


def check_headers(file_name: str, columns: list[str]) -> bool:
    """
    Validate that all required columns for file_name are present.

    Uses a subset check — extra optional columns (e.g. SCADA_CONTROL added
    by some extract variants) are allowed and do not cause a failure.

    Returns True if all required columns are present, False otherwise.
    Missing column names are logged as a WARNING.
    """
    required = set(EXPECTED_HEADERS.get(file_name, []))

    if not required:
        logging.warning("No header definition found for file type: %s", file_name)
        return True  # unknown file type — cannot validate, do not block

    actual  = set(columns)
    missing = required - actual

    if missing:
        logging.warning(
            "%s: missing required columns: %s", file_name, sorted(missing)
        )
        return False

    return True

def getTimestamp():
    return datetime.now(timezone.utc).isoformat()


_PHASE_PERM_MAP = {
    "1230": "ABC",
    "1200": "AB",
    "1030": "AC",
    "0230": "BC",
    "1000": "A",
    "0200": "B",
    "0030": "C",
    "0000": "de-energised",
}

def getPhasePerm(phase_perm):
    if phase_perm is None:
        return "unknown"
    return _PHASE_PERM_MAP.get(phase_perm, f"unknown ({phase_perm})")

def getStateDes(state):
    if state == "1": return "existing installation"
    elif state == "2": return "planned installation"
    else : return "unknown"

def getPhaseDes(phase):
    if phase == "111": return "all three phases"
    if phase == "100": return "phase A only"
    if phase == "010": return "phase B only"
    if phase == "001": return "phase C only"
    if phase == "110": return "phases A and B"
    if phase == "101": return "phases A and C"
    if phase == "011": return "phases B and C"
    return "unknown phase"

def _tofloat(val):
    return float(val) if val not in (None, "") else 0.0

def describe_transformer(row):
    phase   = row["phase"]
    total   = _tofloat(row["total_kva"])
    kva_a   = _tofloat(row["kva_a"])
    kva_b   = _tofloat(row["kva_b"])
    kva_c   = _tofloat(row["kva_c"])

    served   = []
    unserved = []

    if phase[0] == "1": served.append(f"phase A ({kva_a:.0f} kVA)")
    else:               unserved.append("phase A")

    if phase[1] == "1": served.append(f"phase B ({kva_b:.0f} kVA)")
    else:               unserved.append("phase B")

    if phase[2] == "1": served.append(f"phase C ({kva_c:.0f} kVA)")
    else:               unserved.append("phase C")

    served_str   = " and ".join(served)
    unserved_str = " and ".join(unserved)

    return (
        f"The transformer serving this load has a total rating of {total:.0f} kVA, "
        f"all allocated to {served_str}, "
        f"with {unserved_str} unserved."
    )

def describe_billed(row):
    phase    = row["phase"]
    total    = float(row["total_billed"])
    billed_a = float(row["billed_a"])
    billed_b = float(row["billed_b"])
    billed_c = float(row["billed_c"])

    served   = []
    unserved = []

    if phase[0] == "1": served.append(f"phase A ({billed_a:.0f} kWh)")
    else:               unserved.append("phase A")

    if phase[1] == "1": served.append(f"phase B ({billed_b:.0f} kWh)")
    else:               unserved.append("phase B")

    if phase[2] == "1": served.append(f"phase C ({billed_c:.0f} kWh)")
    else:               unserved.append("phase C")

    served_str   = " and ".join(served)
    unserved_str = " and ".join(unserved)

    return (
        f"Billed consumption totals {total:.0f} kWh, "
        f"allocated to {served_str}, "
        f"with {unserved_str} unserved."
    )
