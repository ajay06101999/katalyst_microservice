from dataclasses import dataclass, field

@dataclass
class Vertex:
    node_id : str
    vlevel : str #will be 1 if it is in primary network else flags in the secondary
    con_type : str
    sub_id : str # says which substation that this node is belong

    # mutable fields
    energized : bool = False
    parent : str | None = None
    depth : int | None = None
    phase : str | None = None

    # objects
    loads : list = field(default_factory=list)
    capacitors : list = field(default_factory=list)
    sites : list = field(default_factory=list)
    mpoints : list = field(default_factory = list)

    # Node level summaries
    decision_reason : str | None = None
    blocking_device : str | None = None


    @classmethod
    def from_row(cls, row ) -> "Vertex":
        return cls(
            node_id = row['NID'],
            vlevel = row['VLEVEL'],
            con_type = row["CON_TYPE"],
            sub_id = row['SUB_ID'],
        )
    
            

@dataclass
class Device:
    device_id : str
    line_id: str
    line_end : str
    norm_state : str # It says if the device is open / closed
    phase : str
    dev_cat : str
    dev_type : str

    @property
    def is_open(self) -> bool:
        return self.norm_state == "000"
    
    @classmethod
    def from_row(cls, row ) -> "Device":
        return cls(
            device_id = row['DID'],
            line_id = row['LI_KEY'],
            line_end = row["LINE_END"],
            norm_state = row['NORM_STATE'],
            phase = row['PHASE'],
            dev_cat = row['DEVCAT'],
            dev_type = row['DT_KEY'])
    
@dataclass
class Edge:
    line_id : str
    no_key1 : str
    no_key2 : str
    phase_perm : str
    length : str
    # Every time when the object is created, it create a fresh list. 
    devices : list[Device] = field(default_factory=list)

    @property
    def is_blocked(self) -> bool:
        return any( d.is_open for d in self.devices)
    

    @classmethod
    def from_row(cls, row ) -> "Edge":
        return cls(
            line_id = row['ID'],
            no_key1 = row['NO_KEY_1'],
            no_key2 = row["NO_KEY_2"],
            phase_perm = row['PHASE_PERM'],
            length = row['LENGTH'],
            )

@dataclass
class Load:
    load_id : str
    no_key : str
    phase : str 
    load_type : str
    status : str
    descriptive_loc : str
    sub_area : str
    state : str
    total_kva : str
    kva_a : str
    kva_b : str
    kva_c : str
    total_billed: str
    billed_a : str
    billed_b : str
    billed_c : str
   
    @classmethod
    def from_row(cls , row) -> "Load":
        return cls(
            load_id = row["LOID"],
            no_key = row["NO_KEY"],
            phase = row["PHASE"] ,
            load_type = row["LOTYPE"],
            status = row["STATUS"],
            descriptive_loc = row["DESCRIPTIVE_LOC"],
            sub_area = row["SUB_AREA"],
            state = row["STATE"],
            total_kva   = row["RATING_1"],
            kva_a   = row["RATING_2"],
            kva_b   = row["RATING_3"],
            kva_c   = row["RATING_4"],
            total_billed    = row["BILLED_1"],
            billed_a = row["BILLED_2"],
            billed_b = row["BILLED_3"],
            billed_c = row["BILLED_4"]
        )


@dataclass 
class Capacitor:
    cap_id : str
    no_key : str
    status : str
    dt_key : str
    descriptive_loc : str
    state : str
    isClosed : bool
    reg_v_sens_phase: str
    rating_1 : str
    rating_2 : str
    rating_3 : str
    rating_4 : str


    @classmethod
    def from_row(cls,row) -> "Capacitor":
        return cls(
            cap_id = row["CAID"],
            no_key = row["NO_KEY"],
            status = row["STATUS"],
            dt_key = row["DT_KEY"],
            descriptive_loc = row["DESCRIPTIVE_LOC"],
            state = row["STATE"],
            isClosed = row["PH3PRES"] == "111",
            reg_v_sens_phase = row["REG_V_SENS_PHASE"],
            rating_1 = row["RATING_1"],
            rating_2 = row["RATING_2"],
            rating_3 = row["RATING_3"],
            rating_4 = row["RATING_4"]
           

        )



@dataclass
class Site:
    site_id : str
    no_key : str
    site_type: str
    address : str
    gsiteh : str
    gsitew : str
    gxsite : str
    gysite : str


    @classmethod
    def from_row(cls,row) -> "Site":
        return cls(
            site_id = row["SIID"],
            no_key = row["NO_KEY"],
            site_type = row["TYPE"],
            address = row["ADDRESS"],
            gsiteh = row["GSITEH"],
            gsitew = row["GSITEW"],
            gxsite = row["GXSITE"],
            gysite = row["GYSITE"],
        )



@dataclass
class Mpoint:
    mp_id : str
    mp_name : str
    no_key : str
    line_on : str
    mp_key : str
    state : str

    @classmethod
    def from_row(cls,row) -> "Mpoint":
        return cls(
            mp_id = row["MPID"],
            mp_name = row["MPNAME"],
            no_key = row["NO_KEY"],
            line_on = row["LINE_ON"],
            mp_key = row["MP_KEY"],
            state = row["STATE"],
        )

    