import sys, sqlite3
from pathlib import Path
from typing import (
    List,
    Tuple,
    Dict,
    Set,
    Any,
    Union,
    Callable,
    Literal,
    Optional,
    TypeVar,
    TypedDict,
    NamedTuple,
)
from functools import cache

##Intra-package imports
from file_utils import File_Paths
import cli_gpkg_utils as gpkg_utils
import cli_debug_utils as debug_utils


@cache
def all_wbids():
    db = sqlite3.connect(File_Paths.conus_hydrofabric())
    data = db.execute("SELECT id FROM divides").fetchall()
    db.close()
    return set([d[0] for d in data if isinstance(d[0], str) and "wb" in d[0]])


def check_wbids_valid(wbids: set) -> set:
    geoms = gpkg_utils.get_geom_from_wbids_map(wbids)
    return set([k for k, v in geoms.items() if v is not None])


@cache
def vpu_list() -> list:
    # expected return ['01', '02', '03N', '03S', '03W', '04', '05', '06', '07', '08', '09', '10L', '10U', '11', '12', '13', '14', '15', '16', '17', '18']
    db = sqlite3.connect(File_Paths.conus_hydrofabric())
    # want unique, non-na values for the vpuid field in the network table
    data = db.execute(
        "SELECT DISTINCT vpuid FROM network WHERE vpuid IS NOT NULL"
    ).fetchall()
    db.close()
    return [d[0] for d in data if isinstance(d[0], str) and len(d[0]) > 0]


@cache
def vpu_stats() -> dict:
    db = sqlite3.connect(File_Paths.conus_hydrofabric())
    # names in the network table take the form "prefix-uuid"
    # where prefix is a 2-3 letter code for the type of entry
    # and uuid is a unique identifier
    # we want to count the number of entries for each prefix
    # select the vpuid, the prefix, and the count of the prefix
    # group by the vpuid and the prefix
    query1 = "SELECT vpuid, substr(id, 1, instr(id, '-') - 1) as prefix, count(*) as count FROM network GROUP BY vpuid, prefix"
    data = db.execute(query1).fetchall()
    db.close()
    prefix_counts = {}
    vpu_counts = {}
    vpu_totals = {}
    for vpuid, prefix, count in data:
        if vpuid not in vpu_counts:
            vpu_counts[vpuid] = {}
            vpu_totals[vpuid] = 0
        vpu_counts[vpuid][prefix] = count
        vpu_totals[vpuid] += count
        if prefix not in prefix_counts:
            prefix_counts[prefix] = 0
        prefix_counts[prefix] += count
    return {
        "vpu_counts": vpu_counts,
        "vpu_totals": vpu_totals,
        "prefix_counts": prefix_counts,
    }


@cache
def get_vpu_wbids(vpuid: str) -> set:
    db = sqlite3.connect(File_Paths.conus_hydrofabric())
    query = "SELECT id FROM network WHERE vpuid = ?"
    data = db.execute(query, (vpuid,)).fetchall()
    db.close()
    return set([d[0] for d in data if isinstance(d[0], str) and "wb" in d[0]])


class Gage(NamedTuple):
    wb_id: str
    nex_id: str
    vpu_id: str
    fid: int

    def __str__(self):
        return f"({self.wb_id}, {self.nex_id}, {self.vpu_id}, {self.fid})"

    def __repr__(self):
        return f"Gage({self.wb_id}, {self.nex_id}, {self.vpu_id}, {self.fid})"

    def __hash__(self):
        return hash(self.wb_id)

    @staticmethod
    def valid(wb_id: str, nex_id: str, vpu_id: str, fid: int) -> bool:
        return all(
            [
                isinstance(wb_id, str),
                isinstance(nex_id, str),
                isinstance(vpu_id, str),
                isinstance(fid, int),
            ]
        )


@cache
def get_gages() -> Set[Gage]:
    db = sqlite3.connect(File_Paths.conus_hydrofabric())
    query = "SELECT id as wb_id, nex_id, vpuid as vpu_id, fid FROM hydrolocations WHERE hl_reference = 'gages'"
    data = db.execute(query).fetchall()
    db.close()
    return set([Gage(*d) for d in data if Gage.valid(*d)])


if __name__ == "__main__":
    test_wbids = False
    test_vpuid = False
    test_gages = True
    if test_wbids:
        sample = all_wbids()
        output, used, count = debug_utils.str_sample(sample)
        print(f"all_wbids: loaded {count} wbids")
        print(f"printing {used} wbids:")
        print(output)
        sample = check_wbids_valid(sample)
        output, used, count = debug_utils.str_sample(sample)
        print(f"check_wbids_valid: {count} valid wbids")
        print(f"printing {used} wbids:")
        print(output)
    if test_vpuid:
        sample = vpu_list()
        output, used, count = debug_utils.str_sample(sample)
        print(f"vpu_list: {count} vpuids")
        print(f"printing {used} vpuids:")
        print(output)
        sample = vpu_stats()
        output, used, count = debug_utils.str_sample(sample)
        print(f"vpu_stats: {count} vpuids")
        print(f"printing {used} vpuids:")
        print(output)
        sample = get_vpu_wbids("01")
        output, used, count = debug_utils.str_sample(sample)
        print(f"get_vpu_wbids: {count} wbids")
        print(f"printing {used} wbids:")
        print(output)
    if test_gages:
        sample = get_gages()
        output, used, count = debug_utils.str_sample(sample)
        print(f"get_gages: {count} gages")
        print(f"printing {used} gages:")
        print(output)
        sample = list(sample)[0]
        print(f"sample gage: {sample}")
        print(f"sample gage hash: {hash(sample)}")
        print(f"sample gage valid: {Gage.valid(*sample)}")
        print(f"sample gage str: {str(sample)}")
        print(f"sample gage repr: {repr(sample)}")
