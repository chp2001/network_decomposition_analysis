import sys, sqlite3
from pathlib import Path
from typing import List, Tuple, Dict, Any, Union
from functools import cache

##Intra-package imports
from file_utils import File_Paths
import cli_gpkg_utils as gpkg_utils


@cache
def all_wbids():
    db = sqlite3.connect(File_Paths.conus_hydrofabric())
    data = db.execute("SELECT id FROM divides").fetchall()
    db.close()
    return set([d[0] for d in data if isinstance(d[0], str) and "wb" in d[0]])

def check_wbids_valid(wbids:set)->set:
    geoms = gpkg_utils.get_geom_from_wbids_map(wbids)
    return set([k for k, v in geoms.items() if v is not None])