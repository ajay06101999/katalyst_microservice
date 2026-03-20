from utils.helpers import getPhaseDes, getStateDes, describe_transformer, describe_billed, getPhasePerm


# ---------------------------------------------------------------------------
# Node-level context builders
# ---------------------------------------------------------------------------

def buildLoadContext(loads, node_id):
    load_description = []
    for load in loads:
        load_description.append(
            f'This load point - "{load["load_id"]}" is attached to node - "{node_id}", '
            f'located at "{load["descriptive_loc"]}", in sub-area "{load["sub_area"]}" \n'
        )
        load_description.append(
            f'This load is an {getStateDes(load["state"])}, served on '
            f'{getPhaseDes(load["phase"])}-{load["phase"]}.\n'
        )
        load_description.append(describe_transformer(load) + "\n")
        load_description.append(describe_billed(load) + "\n")
        load_description.append("\n")
    return "".join(load_description)


def buildCapacitorContext(capacitors):
    capacitor_description = []
    for cap in capacitors:
        capacitor_description.append(
            f'Capacitor {cap["cap_id"]} is attached to node {cap["no_key"]}, '
            f'located at {cap["descriptive_loc"]}.\n'
        )
        capacitor_description.append(f'This is an {getStateDes(cap["state"])}.\n')
        capacitor_description.append(f'It is connected on {getPhaseDes(cap["status"])}.\n')
        if cap["isClosed"]:
            capacitor_description.append(
                f'Capacitor {cap["cap_id"]} closed and online — all three phases are actively present.\n'
            )
        capacitor_description.append(
            f'The bank has a total rating of {cap["rating_1"]} kVAR, divided into '
            f'{cap["rating_2"]} kVAR, {cap["rating_3"]} kVAR and {cap["rating_4"]} kVAR '
            f'across phases A, B, and C.\n'
        )
        capacitor_description.append(
            f'Automatic voltage regulation is sensed on phase {cap["reg_v_sens_phase"]}\n'
        )
    return "".join(capacitor_description)


def _parseSiteOrigin(address: str) -> str:
    if address.startswith("switch_gear"):
        return "switchgear/device site"
    elif address.startswith("junction"):
        return "junction site"
    elif address.startswith("substation"):
        return "substation site"
    else:
        return "site"


def buildSiteContext(sites):
    site_description = []
    for site in sites:
        origin = _parseSiteOrigin(site["address"])
        site_description.append(f'Site "{site["site_id"]}" is a {origin} attached to node "{site["no_key"]}".\n')
        site_description.append(
            f'It has a bounding box of {site["gsiteh"]} (height) x {site["gsitew"]} (width) in schematic units.\n'
        )
        site_description.append(
            f'Its schematic anchor point is at coordinates ({site["gxsite"]}, {site["gysite"]}).\n'
        )
        site_description.append("\n")
    return "".join(site_description)


def buildMpointContext(mpoints):
    mpoint_description = []
    for mp in mpoints:
        mpoint_description.append(
            f'Meter point "{mp["mp_id"]}" ({mp["mp_name"]}) is located at node "{mp["no_key"]}".\n'
        )
        if mp["line_on"]:
            mpoint_description.append(f'It is placed on line "{mp["line_on"]}".\n')
        else:
            mpoint_description.append("No line association recorded for this meter point.\n")
        mpoint_description.append(f'SCADA point key: {mp["mp_key"]}.\n')
        mpoint_description.append(f'This is an {getStateDes(mp["state"])}.\n')
        mpoint_description.append("\n")
    return "".join(mpoint_description)


# ---------------------------------------------------------------------------
# Chunk builders
# ---------------------------------------------------------------------------

def node_chunk(doc: dict) -> str:
    node_id         = doc["node_id"]
    feeder_id       = doc["feeder_id"]
    depth           = doc["depth"]
    energized       = doc["energized"]
    decision_reason = doc["decision_reason"]
    blocking_device = doc["blocking_device"]
    parent_node     = doc["parent"]
    vlevel          = doc["vlevel"]
    loads           = doc["loads"]
    capacitors      = doc["capacitors"]
    sites           = doc["sites"]
    mpoints         = doc["mpoints"]
    sub_id          = doc["sub_id"]
    phase           = doc["phase"]

    return f"""
Node {node_id} in feeder {feeder_id} at depth {depth}.
Status: {"energized" if energized else "de-energized"}.
Decision: {decision_reason}.
Blocking device: {blocking_device or "No blocking devices"}.
Parent: {parent_node}. Voltage level: {vlevel}. Substation: {sub_id}.
Incoming conductor phase: {getPhasePerm(phase)}.

Loads:
{"No loads present in this vertex" if not loads else f"{len(loads)} load(s) present in this vertex"}
{buildLoadContext(loads, node_id)}
Capacitors:
{"No capacitors present in this vertex" if not capacitors else f"{len(capacitors)} capacitor(s) present in this vertex"}
{buildCapacitorContext(capacitors)}
Sites:
{"No sites in this vertex" if not sites else f"{len(sites)} site(s) present in this vertex"}
{buildSiteContext(sites)}
Mpoints:
{"No mpoints in this vertex" if not mpoints else f"{len(mpoints)} mpoint(s) present in this vertex"}
{buildMpointContext(mpoints)}"""


def feeder_summary_chunk(stats: dict) -> str:
    feeder_id       = stats["feeder_id"]
    feeder_name     = stats["feeder_name"]
    op_dist         = stats["op_dist"]
    sub_name        = stats["sub_name"]
    sub_id          = stats["sub_id"]
    district        = stats["district"]
    trace_id        = stats["trace_id"]
    root_node       = stats["root_node"]
    total_nodes     = stats["total_nodes"]
    total_edges     = stats["total_edges"]
    total_devices   = stats["total_devices"]
    max_depth       = stats["max_depth"]
    energized_nodes    = stats["energized_nodes"]
    de_energized_nodes = stats["de_energized_nodes"]
    directly_blocked   = stats["directly_blocked"]
    propagated         = stats["propagated"]
    open_device_count  = stats["open_device_count"]
    closed_device_count = stats["closed_device_count"]
    open_devices    = stats["open_devices"]
    devcat_counts   = stats["devcat_counts"]
    devtype_counts  = stats["devtype_counts"]
    total_loads     = stats["total_loads"]
    total_capacitors = stats["total_capacitors"]
    total_sites     = stats["total_sites"]
    total_mpoints   = stats["total_mpoints"]

    energized_pct    = (energized_nodes    / total_nodes * 100) if total_nodes else 0.0
    de_energized_pct = (de_energized_nodes / total_nodes * 100) if total_nodes else 0.0

    open_device_lines = [
        f"  Device {d['device_id']} (category: {d['dev_cat']}, type: {d['dev_type']}) on line {d['line_id']}."
        for d in open_devices
    ]
    open_device_section = (
        "\n".join(open_device_lines) if open_device_lines
        else "  No open devices — feeder is fully energized."
    )

    devcat_lines  = "\n".join(f"  {cat}: {cnt}" for cat, cnt in sorted(devcat_counts.items(), key=lambda x: -x[1]))
    devtype_lines = "\n".join(f"  {dt}: {cnt}"  for dt,  cnt in sorted(devtype_counts.items(), key=lambda x: -x[1]))

    return f"""FEEDER SUMMARY — {feeder_name}
Trace ID           : {trace_id}
Feeder             : {feeder_id} | Operating District: {op_dist}
Substation         : {sub_name} (SUB_ID: {sub_id}) | District: {district}
Root node          : {root_node}

=== NETWORK TOPOLOGY ===
Total nodes           : {total_nodes}
Total conductor spans : {total_edges}
Total devices         : {total_devices}
Max depth from root   : {max_depth}

=== ENERGIZATION STATUS ===
Energized nodes    : {energized_nodes} ({energized_pct:.1f}%)
De-energized nodes : {de_energized_nodes} ({de_energized_pct:.1f}%)

De-energization breakdown:
  Directly blocked by open device    : {directly_blocked}
  Propagated from de-energized parent: {propagated}

=== OPEN DEVICES (supply boundary points) ===
{open_device_count} open device(s) creating supply boundaries:
{open_device_section}

=== DEVICE INVENTORY ===
Total devices   : {total_devices}
  Open (blocking) : {open_device_count}
  Closed (normal) : {closed_device_count}

By device category (DEVCAT):
{devcat_lines}

By device type (DT_KEY):
{devtype_lines}

=== ASSETS IN TRACE ===
Total loads      : {total_loads}
Total capacitors : {total_capacitors}
Total sites      : {total_sites}
Total mpoints    : {total_mpoints}
"""
