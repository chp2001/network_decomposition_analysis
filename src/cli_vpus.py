import sys, sqlite3
from pathlib import Path
from typing import List, Tuple, Dict, Any, Union
from functools import cache

##Intra-package imports
from file_utils import File_Paths

ONCE = (True,)
RENDER = False


@cache
def vpu_list()->list:
    #expected return ['01', '02', '03N', '03S', '03W', '04', '05', '06', '07', '08', '09', '10L', '10U', '11', '12', '13', '14', '15', '16', '17', '18']
    db = sqlite3.connect(File_Paths.conus_hydrofabric())
    #want unique, non-na values for the vpu field in the network table
    data = db.execute("SELECT DISTINCT vpu FROM network WHERE vpu IS NOT NULL").fetchall()
    db.close()
    return [d[0] for d in data if isinstance(d[0], str) and len(d[0]) > 0]

@cache
def vpu_stats()->dict:
    db = sqlite3.connect(File_Paths.conus_hydrofabric())
    #names in the network table take the form "prefix-uuid"
    # where prefix is a 2-3 letter code for the type of entry
    # and uuid is a unique identifier
    # we want to count the number of entries for each prefix
    # select the vpu, the prefix, and the count of the prefix
    # group by the vpu and the prefix
    query1 = "SELECT vpu, substr(id, 1, instr(id, '-') - 1) as prefix, count(*) as count FROM network GROUP BY vpu, prefix"
    data = db.execute(query1).fetchall()
    db.close()
    prefix_counts = {}
    vpu_counts = {}
    vpu_totals = {}
    for vpu, prefix, count in data:
        if vpu not in vpu_counts:
            vpu_counts[vpu] = {}
            vpu_totals[vpu] = 0
        vpu_counts[vpu][prefix] = count
        vpu_totals[vpu] += count
        if prefix not in prefix_counts:
            prefix_counts[prefix] = 0
        prefix_counts[prefix] += count
    return {
        "vpu_counts": vpu_counts,
        "vpu_totals": vpu_totals,
        "prefix_counts": prefix_counts
    }

@cache
def get_vpu_wbids(vpu:str)->set:
    db = sqlite3.connect(File_Paths.conus_hydrofabric())
    query = "SELECT id FROM network WHERE vpu = ?"
    data = db.execute(query, (vpu,)).fetchall()
    db.close()
    return set([d[0] for d in data if isinstance(d[0], str) and "wb" in d[0]])