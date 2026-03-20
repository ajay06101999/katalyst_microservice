"""
Extract Data Model Reference
============================
TypedDict definitions for every ADMS CSV extract file.

All fields are `str` because every extract is loaded with dtype=str.
Type comments describe the semantic type of the value.

Usage
-----
    from Entities.schemas import NodeRow, LineRow, DeviceRow

    node: NodeRow = df.iloc[0].to_dict()

Key relationships at a glance
------------------------------
    NODE.NID          ← graph vertex identifier
    LINE.NO_KEY_1/2   → NODE.NID          (edge endpoints)
    DEVICE.LI_KEY     → LINE.ID           (device sits on this line)
    DEVICE.LINE_END   → "1" or "2"        (which end-node the device is at)
    SOURCE.NO_KEY     → NODE.NID          (source attached to this node)
    FEEDER.FIRST_NODE_ID → NODE.NID       (feeder root / pseudo-source node)
    FEEDER.FIRST_LINE_ID → LINE.ID        (first conductor out of root)
    LOAD.NO_KEY       → NODE.NID
    CAPACITOR.NO_KEY  → NODE.NID
    SITE.NO_KEY       → NODE.NID
    MPOINT.NO_KEY     → NODE.NID
    MPOINT.LINE_ON    → LINE.ID

NORM_STATE encoding (DEVICE, SOURCE)
--------------------------------------
    "000"            → device is OPEN  (breaks the circuit)
    any phase code   → device is CLOSED (e.g. "1230" = ABC)

STYPE encoding (SOURCE)
------------------------
    "0"  → pseudo-source  (ADMS virtual node, feeder entry point)
    "1"  → swing source   (real substation transformer, DFS root)
    "2"  → generation     (DER / generator)

PHASE_PERM encoding (LINE, DEVICE, SOURCE)
-------------------------------------------
    "1230" → ABC    "1200" → AB    "1030" → AC
    "0230" → BC     "1000" → A     "0200" → B
    "0030" → C      "0000" → de-energised
"""

from typing import TypedDict


# ---------------------------------------------------------------------------
# NODE.csv  — graph vertices
# ---------------------------------------------------------------------------

class NodeRow(TypedDict):
    NFPOS:      str   # position index — same value as NID
    NID:        str   # PRIMARY KEY — graph node identifier
    ABB_INT_ID: str   # internal GIS ID (same as NID in practice)
    NNAME:      str   # human-readable node label
    XN_1:       str   # actual UTM X coordinate
    YN_1:       str   # actual UTM Y coordinate
    XN_2:       str   # schematic X coordinate
    YN_2:       str   # schematic Y coordinate
    NBITS:      str   # encoding bits (topology flags)
    CON_TYPE:   str   # connection type: series node vs shunt node
    SG_KEY_1:   str   # switchgear key — "41" = normal external node
                      #                  other values = inside switchgear
    SUB_AREA:   str   # sub-area / operating district code
    STATE:      str   # "1" = Existing, "2" = Planned
    VLEVEL:     str   # voltage level code ("1" = primary distribution)
    SUB_ID:     str   # FK → SUBSTATION.SUB_ID
    SITE_KEY:   str   # FK → SITE.SIID  (empty if no associated site)
    NANNOPOS_1: str   # annotation position X
    NANNOPOS_2: str   # annotation position Y
    SECONDARY:  str   # non-empty = secondary voltage node


# ---------------------------------------------------------------------------
# LINE.csv  — graph edges (conductors / spans)
# ---------------------------------------------------------------------------

class LineRow(TypedDict):
    FPOS:       str   # position index — same value as ID
    ID:         str   # PRIMARY KEY — graph edge identifier
    ABB_INT_ID: str   # internal GIS ID (same as ID in practice)
    NAME:       str   # conductor name (e.g. "OH Spaced 4/0 AL")
    NO_KEY_1:   str   # FK → NODE.NID — first endpoint of this edge
    NO_KEY_2:   str   # FK → NODE.NID — second endpoint of this edge
    PA_KEY_1:   str   # FK → PATH.PAFPOS — wire routing path start
    PA_KEY_2:   str   # FK → PATH.PAFPOS — wire routing path end (empty if straight)
    PHASE_PERM: str   # 4-digit phase code (see header for encoding)
    LINE_TYPE:  str   # FK → LineTypes reference table (conductor spec code)
    BITS:       str   # encoding bits
    SUB_AREA:   str   # sub-area code
    STATE:      str   # "1" = Existing
    LENGTH:     str   # span length in feet (int-valued string)
    ANNOPOS_1:  str   # annotation position X
    ANNOPOS_2:  str   # annotation position Y


# ---------------------------------------------------------------------------
# DEVICE.csv  — switchable devices placed on lines
#              (fuses, reclosers, sectionalizers, regulators, transformers)
# ---------------------------------------------------------------------------

class DeviceRow(TypedDict):
    DFPOS:          str   # position index — same value as DID
    DID:            str   # PRIMARY KEY — device identifier
    ABB_INT_ID:     str   # internal GIS ID
    CONTROLLED:     str   # SCADA-controllable flag
    DNAME:          str   # device name / label
    DEVCAT:         str   # device category code (fuse, switch, regulator …)
    DT_KEY:         str   # FK → DevTypes reference table (specific device type)
    XD_1:           str   # actual UTM X coordinate
    YD_1:           str   # actual UTM Y coordinate
    XD_2:           str   # schematic X coordinate
    YD_2:           str   # schematic Y coordinate
    LI_KEY:         str   # FK → LINE.ID — the line this device is placed on
    LINE_END:       str   # which end of the line: "1" → NO_KEY_1 node
                          #                        "2" → NO_KEY_2 node
    PHASE:          str   # phase code of this device
    DEVICESIZE:     str   # device rating / size
    CURRENTCTA:     str   # current CT value phase A
    CURRENTCTB:     str   # current CT value phase B
    CURRENTCTC:     str   # current CT value phase C
    NORM_STATE:     str   # open/closed state — "000" = OPEN, phase code = CLOSED
    STATUS:         str   # same as NORM_STATE (redundant copy)
    DESCRIPTIVE_LOC:str   # street address / location description
    SUB_AREA:       str   # sub-area code
    STATE:          str   # "1" = Existing
    ATO_KEY:        str   # ATO (asset) identifier
    TOWNSHIP:       str   # tax district / township
    ANNOPOS_1:      str   # annotation position X
    ANNOPOS_2:      str   # annotation position Y
    TAPSIDE:        str   # transformer tap side ("2" for regulators)
    MINBANDWA:      str   # regulator minimum band width phase A
    MINBANDWB:      str   # regulator minimum band width phase B
    MINBANDWC:      str   # regulator minimum band width phase C
    MAXBANDWA:      str   # regulator maximum band width phase A
    MAXBANDWB:      str   # regulator maximum band width phase B
    MAXBANDWC:      str   # regulator maximum band width phase C
    REQVOLTS:       str   # regulator required voltage setpoint
    BREAKAMPS:      str   # breaker interrupt current rating


# ---------------------------------------------------------------------------
# SOURCE.csv  — voltage sources (feeder roots, DER generators)
# ---------------------------------------------------------------------------

class SourceRow(TypedDict):
    SOID:       str   # PRIMARY KEY — source identifier
    SONAME:     str   # source name
    SOFPOS:     str   # position index
    ABB_INT_ID: str   # internal GIS ID
    NO_KEY:     str   # FK → NODE.NID — node this source is attached to
    VLEVEL:     str   # voltage level code
    STYPE:      str   # source type: "0"=pseudo, "1"=swing (root), "2"=generation
    SCOLIND:    str   # display colour index
    SG_KEY:     str   # switchgear key: "302"=swing, "301"=pseudo, "303-305"=DER
    STATE:      str   # state code
    STATUS:     str   # status code
    KWGEN:      str   # generator output in KW (DER only, else "0")
    MAXKVAR:    str   # max reactive power
    MINKVAR:    str   # min reactive power
    MAXCAP:     str   # maximum capacity
    EMERGCAP:   str   # emergency capacity
    POSSEQR:    str   # positive sequence resistance
    POSSEQX:    str   # positive sequence reactance
    ZEROSEQR:   str   # zero sequence resistance
    ZEROSEQX:   str   # zero sequence reactance
    NEGSEQX:    str   # negative sequence reactance
    ANNOPOS_1:  str   # annotation position X
    ANNOPOS_2:  str   # annotation position Y
    SYM_POS_1:  str   # symbol position X
    SYM_POS_2:  str   # symbol position Y
    DISTRICT:   str   # operating district
    SVPU_T:     str   # source voltage per unit (total)
    NOMPHANG_A: str   # nominal phase angle A (degrees)
    NOMPHANG_B: str   # nominal phase angle B (degrees)
    NOMPHANG_C: str   # nominal phase angle C (degrees)
    SVPU_A:     str   # source voltage per unit phase A
    SVPU_B:     str   # source voltage per unit phase B
    SVPU_C:     str   # source voltage per unit phase C
    DERTYPE:    str   # DER fuel type code (blank for substation sources)
    LINE_ON:    str   # FK → LINE.ID — DER attached to this line (blank for SB)
    PHASE:      str   # phase code
    NORM_STATE: str   # "111" for substation sources


# ---------------------------------------------------------------------------
# FEEDER.csv  — feeder metadata (exactly ONE data row per extract file)
# ---------------------------------------------------------------------------

class FeederRow(TypedDict):
    FIRST_LINE_ID:  str   # FK → LINE.ID — first conductor out of the feeder root
    FIRST_NODE_ID:  str   # FK → NODE.NID — feeder root (pseudo-source node)
    ID:             str   # station breaker GIS device ID
    NAME:           str   # feeder name / identifier
    SITE:           str   # site reference
    SUB_ID:         str   # FK → SUBSTATION.SUB_ID


# ---------------------------------------------------------------------------
# LOAD.csv  — customer load points attached to nodes
# ---------------------------------------------------------------------------

class LoadRow(TypedDict):
    LOFPOS:         str   # position index
    LOID:           str   # PRIMARY KEY — load identifier
    LONAME:         str   # load name
    ABB_INT_ID:     str   # internal GIS ID
    NO_KEY:         str   # FK → NODE.NID — node this load hangs off
    STATUS:         str   # status code
    SG_KEY:         str   # switchgear key
    BITS:           str   # encoding bits
    BILLED_1:       str   # billed kWh period 1
    BILLED_2:       str   # billed kWh period 2
    BILLED_3:       str   # billed kWh period 3
    BILLED_4:       str   # billed kWh period 4
    CUSTNO_1:       str   # customer count period 1
    CUSTNO_2:       str   # customer count period 2
    CUSTNO_3:       str   # customer count period 3
    CUSTNO_4:       str   # customer count period 4
    PFACT_1:        str   # power factor period 1
    PFACT_2:        str   # power factor period 2
    PFACT_3:        str   # power factor period 3
    PFACT_4:        str   # power factor period 4
    RATING_1:       str   # transformer kVA rating period 1
    RATING_2:       str   # transformer kVA rating period 2
    RATING_3:       str   # transformer kVA rating period 3
    RATING_4:       str   # transformer kVA rating period 4
    PHASE:          str   # phase served
    STATE:          str   # "1" = Existing
    DESCRIPTIVE_LOC:str   # street address / location description
    TAP_1:          str   # transformer tap position
    LOTYPE:         str   # load type code
    ANNOPOS_1:      str   # annotation position X
    ANNOPOS_2:      str   # annotation position Y
    SYM_POS_1:      str   # symbol position X
    SYM_POS_2:      str   # symbol position Y
    SUB_AREA:       str   # sub-area code


# ---------------------------------------------------------------------------
# CAPACITOR.csv  — capacitor banks attached to nodes
# ---------------------------------------------------------------------------

class CapacitorRow(TypedDict):
    CAFPOS:           str   # position index
    CAID:             str   # PRIMARY KEY — capacitor identifier
    ABB_INT_ID:       str   # internal GIS ID
    CANAME:           str   # capacitor name
    NO_KEY:           str   # FK → NODE.NID — node this capacitor is on
    DT_KEY:           str   # FK → DevTypes reference table
    RATING_1:         str   # kVAR rating bank 1
    RATING_2:         str   # kVAR rating bank 2
    RATING_3:         str   # kVAR rating bank 3
    RATING_4:         str   # kVAR rating bank 4
    REG_V_SENS_PHASE: str   # voltage sensing phase for regulation
    DESCRIPTIVE_LOC:  str   # location description
    PH3PRES:          str   # three-phase present flag
    STATE:            str   # "1" = Existing
    STATUS:           str   # status code
    ANNO_POS_1:       str   # annotation position X
    ANNO_POS_2:       str   # annotation position Y


# ---------------------------------------------------------------------------
# SITE.csv  — physical sites (poles, pads, vaults, substations)
# ---------------------------------------------------------------------------

class SiteRow(TypedDict):
    SIID:       str   # PRIMARY KEY — site identifier
    SINAME:     str   # site name
    SIFPOS:     str   # position index
    ABB_INT_ID: str   # internal GIS ID
    NO_KEY:     str   # FK → NODE.NID — node at this site
    SG_KEY:     str   # switchgear key
    TYPE:       str   # site type code (pole, pad, vault, substation …)
    GSITEH:     str   # site height
    GSITEW:     str   # site width
    GXSITE:     str   # site X coordinate
    GYSITE:     str   # site Y coordinate
    ADDRESS:    str   # street address
    ANNOPOS_1:  str   # annotation position X
    ANNOPOS_2:  str   # annotation position Y


# ---------------------------------------------------------------------------
# SUBSTATION.csv  — substation metadata
# ---------------------------------------------------------------------------

class SubstationRow(TypedDict):
    DISTRICT:   str   # operating district code
    ID:         str   # PRIMARY KEY — substation identifier
    NAME:       str   # substation name
    SUB_ID:     str   # substation numeric ID (FK target for NODE.SUB_ID)


# ---------------------------------------------------------------------------
# MPOINT.csv  — SCADA measurement points (optional — only in SCADA extracts)
# ---------------------------------------------------------------------------

class MpointRow(TypedDict):
    MPFPOS:     str   # position index
    MPID:       str   # PRIMARY KEY — measurement point identifier
    MPNAME:     str   # measurement point name
    NO_KEY:     str   # FK → NODE.NID — node this measurement is at
    LINE_ON:    str   # FK → LINE.ID  — line this measurement is on (may be empty)
    MP_KEY:     str   # SCADA point key
    STATE:      str   # state code
    ABB_INT_ID: str   # internal GIS ID
    ANNOPOS_1:  str   # annotation position X
    ANNOPOS_2:  str   # annotation position Y
    SG_KEY:     str   # switchgear key


# ---------------------------------------------------------------------------
# PATH.csv  — intermediate wire routing coordinates
#             NOT needed for graph topology — only for rendering
# ---------------------------------------------------------------------------

class PathRow(TypedDict):
    PAFPOS:     str   # FK → LINE.PA_KEY_1 or PA_KEY_2 (links path to a line)
    NEXTP:      str   # sequence index within this path
    XDIFF:      str   # X offset from previous point
    YDIFF:      str   # Y offset from previous point


# ---------------------------------------------------------------------------
# Convenience type aliases  (use these in function signatures)
# ---------------------------------------------------------------------------

#  extract_data["node_data"]    → pd.DataFrame  whose rows conform to NodeRow
#  extract_data["line_data"]    → pd.DataFrame  whose rows conform to LineRow
#  extract_data["device_data"]  → pd.DataFrame  whose rows conform to DeviceRow
#  … and so on for each file

__all__ = [
    "NodeRow",
    "LineRow",
    "DeviceRow",
    "SourceRow",
    "FeederRow",
    "LoadRow",
    "CapacitorRow",
    "SiteRow",
    "SubstationRow",
    "MpointRow",
    "PathRow",
]
