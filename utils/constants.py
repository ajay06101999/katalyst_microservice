FILE_NAMES: list[str] = [
    "CAPACITOR",
    "DEVICE",
    "FEEDER",
    "LINE",
    "LOAD",
    "MPOINT",
    "NODE",
    "PATH",
    "SITE",
    "SOURCE",
    "SUBSTATION",
]




EXPECTED_HEADERS: dict[str, list[str]] = {
    "CAPACITOR": [
        "CAFPOS", "CAID", "ABB_INT_ID", "CANAME", "NO_KEY", "DT_KEY",
        "RATING_1", "RATING_2", "RATING_3", "RATING_4", "REG_V_SENS_PHASE",
        "DESCRIPTIVE_LOC", "PH3PRES", "STATE", "STATUS", "ANNO_POS_1", "ANNO_POS_2",
    ],
    "DEVICE": [
        "DFPOS", "DID", "ABB_INT_ID", "CONTROLLED", "DNAME", "DEVCAT", "DT_KEY",
        "XD_1", "YD_1", "XD_2", "YD_2", "LI_KEY", "LINE_END", "PHASE", "DEVICESIZE",
        "CURRENTCTA", "CURRENTCTB", "CURRENTCTC", "NORM_STATE", "STATUS",
        "DESCRIPTIVE_LOC", "SUB_AREA", "STATE", "ATO_KEY", "TOWNSHIP",
        "ANNOPOS_1", "ANNOPOS_2", "TAPSIDE",
        "MINBANDWA", "MINBANDWB", "MINBANDWC",
        "MAXBANDWA", "MAXBANDWB", "MAXBANDWC",
        "REQVOLTS", "BREAKAMPS",
    ],
    "FEEDER": [
        "FIRST_LINE_ID", "FIRST_NODE_ID", "ID", "NAME", "SITE", "SUB_ID",
    ],
    "LINE": [
        "FPOS", "ID", "ABB_INT_ID", "NAME", "NO_KEY_1", "NO_KEY_2",
        "PA_KEY_1", "PA_KEY_2", "PHASE_PERM", "LINE_TYPE", "BITS",
        "SUB_AREA", "STATE", "LENGTH", "ANNOPOS_1", "ANNOPOS_2",
    ],
    "LOAD": [
        "LOFPOS", "LOID", "LONAME", "ABB_INT_ID", "NO_KEY", "STATUS", "SG_KEY", "BITS",
        "BILLED_1", "BILLED_2", "BILLED_3", "BILLED_4",
        "CUSTNO_1", "CUSTNO_2", "CUSTNO_3", "CUSTNO_4",
        "PFACT_1", "PFACT_2", "PFACT_3", "PFACT_4",
        "RATING_1", "RATING_2", "RATING_3", "RATING_4",
        "PHASE", "STATE", "DESCRIPTIVE_LOC", "TAP_1", "LOTYPE",
        "ANNOPOS_1", "ANNOPOS_2", "SYM_POS_1", "SYM_POS_2", "SUB_AREA",
    ],
    "MPOINT": [
        "MPFPOS", "MPID", "MPNAME", "NO_KEY", "LINE_ON", "MP_KEY",
        "STATE", "ABB_INT_ID", "ANNOPOS_1", "ANNOPOS_2", "SG_KEY",
    ],
    "NODE": [
        "NFPOS", "NID", "ABB_INT_ID", "NNAME", "XN_1", "YN_1", "XN_2", "YN_2",
        "NBITS", "CON_TYPE", "SG_KEY_1", "SUB_AREA", "STATE", "VLEVEL", "SUB_ID",
        "SITE_KEY", "NANNOPOS_1", "NANNOPOS_2", "SECONDARY",
    ],
    "PATH": [
        "PAFPOS", "NEXTP", "XDIFF", "YDIFF",
    ],
    "SITE": [
        "SIID", "SINAME", "SIFPOS", "ABB_INT_ID", "NO_KEY", "SG_KEY", "TYPE",
        "GSITEH", "GSITEW", "GXSITE", "GYSITE", "ADDRESS", "ANNOPOS_1", "ANNOPOS_2",
    ],
    "SOURCE": [
        "SOID", "SONAME", "SOFPOS", "ABB_INT_ID", "NO_KEY", "VLEVEL", "STYPE",
        "SCOLIND", "SG_KEY", "STATE", "STATUS", "KWGEN", "MAXKVAR", "MINKVAR",
        "MAXCAP", "EMERGCAP", "POSSEQR", "POSSEQX", "ZEROSEQR", "ZEROSEQX", "NEGSEQX",
        "ANNOPOS_1", "ANNOPOS_2", "SYM_POS_1", "SYM_POS_2",
        "DISTRICT", "SVPU_T", "NOMPHANG_A", "NOMPHANG_B", "NOMPHANG_C",
        "SVPU_A", "SVPU_B", "SVPU_C", "DERTYPE", "LINE_ON", "PHASE", "NORM_STATE",
    ],
    "SUBSTATION": [
        "DISTRICT", "ID", "NAME", "SUB_ID",
    ],
}

