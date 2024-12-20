import os, sys, json, pickle
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
)

import geopandas

from file_utils import File_Paths
import cli_graph_utils as graph_utils
import cli_access_utils as access_utils
import cli_debug_utils as debug_utils
import cli_gpkg_utils as gpkg_utils
import cli_geom_manip as geom_manip

import copy, time


def get_last_nodes_in_hydrofabric() -> List[str]:
    graph = graph_utils.get_graph()
    all_wbids = access_utils.all_wbids()
    subgraph_attrs = graph_utils.subgraphs_with_attributes(graph, all_wbids)
    non_tnx = [s for s in subgraph_attrs if not s[2]["has_tnx"]]
    non_cnx = [s for s in non_tnx if not s[2]["has_cnx"]]
    last_nodes = [v for s in non_cnx for v in s[2]["last_node"]]
    last_nodes.sort()
    return last_nodes


def graph_gage_wbs() -> None:
    gages = access_utils.get_gages()
    wbids = [g.wb_id for g in gages]
    wbs = gpkg_utils.get_geom_from_wbids_map(wbids)
    geoms = [v for k, v in wbs.items() if v is not None]
    debug_utils.debug_geoplot_geom(
        geoms, geom_manip.geom_get_bounds(geoms), "gages_map.png"
    )


def get_graph_gage_components() -> Dict[str, List[str]]:
    gages = access_utils.get_gages()
    print(f"Got gages. {len(gages)}")
    graph = graph_utils.get_graph()
    print("Got graph")
    # copy the graph
    graph_copy = copy.deepcopy(graph)
    print("Copied graph")
    # get the wbids
    wbids = [g.wb_id for g in gages]
    # get the wbid nodes
    before = time.perf_counter()
    all_wbids = access_utils.all_wbids()
    after = time.perf_counter()
    print(f"Got {len(all_wbids)} all wbids in {after-before} seconds")
    before = time.perf_counter()
    # assert all(
    #     [w in all_wbids for w in wbids]
    # ), f"Not all wbids are in the hydrofabric? {len(wbids)} vs {len([w for w in wbids if w in all_wbids])}"
    wbids = [w for w in wbids if w in all_wbids]
    after = time.perf_counter()
    print(f"Checked wbids in all wbids in {after-before} seconds")
    before = time.perf_counter()
    all_wbid_nodes = graph_copy.vs.select(name_in=all_wbids)
    after = time.perf_counter()
    print(f"Got {len(all_wbid_nodes)} all wbid nodes in {after-before} seconds")
    before = time.perf_counter()
    wbid_to_node = {v["name"]: v for v in all_wbid_nodes}
    after = time.perf_counter()
    print(f"Got {len(wbid_to_node)} wbid to node map in {after-before} seconds")
    before = time.perf_counter()
    wbid_nodes = [wbid_to_node[wbid] for wbid in wbids]
    after = time.perf_counter()
    print(f"Got {len(wbid_nodes)} wbid nodes in {after-before} seconds")
    # sever gage downstream connections
    edges_for_removal = []
    for n in wbid_nodes:
        for succ in graph_copy.successors(n):
            edges_for_removal.append(
                (n.index, succ.index if not isinstance(succ, int) else succ)
            )
    graph_copy.delete_edges(edges_for_removal)
    print("Severed gage downstream connections")
    # get the subgraphs for each gage
    # first, decompose. then get the subgraph that contains the gage
    subgraphs = graph_copy.decompose(minelements=1, mode="weak")
    print(f"Got subgraphs. {len(subgraphs)}")
    before = time.perf_counter()
    gage_subgraphs = {}
    for gage in wbid_nodes:
        component = graph_copy.subcomponent(gage)
        component: List[int]
        nodes = [graph_copy.vs[i] for i in component]
        names = [
            n["name"]
            for n in nodes
            if n["name"] is not None and n["name"].startswith("wb")
        ]
        gage_subgraphs[gage["name"]] = names
    after = time.perf_counter()
    print(f"Got gage subgraphs. {len(gage_subgraphs)} in {after-before} seconds")
    # get the wbids in each subgraph

    before = time.perf_counter()
    gage_components = {}

    for gage, subgraph in gage_subgraphs.items():
        gage_components[gage] = [n for n in subgraph if n in all_wbids]
    after = time.perf_counter()
    print(
        f"Filtered gage components into wbids. {len(gage_components)} in {after-before} seconds"
    )
    return gage_components


def plot_graph_gage_components() -> None:
    gage_components = get_graph_gage_components()
    print(f"Got gage components. {len(gage_components)}")
    component_geoms = {}
    all_wbids = access_utils.all_wbids()
    geoms = gpkg_utils.get_geom_from_wbids_map(all_wbids)
    for gage, components in gage_components.items():
        component_geoms[gage] = [geoms[wbid] for wbid in components if wbid in geoms]
    print(f"Got component geoms. {len(component_geoms)}")
    merged_geoms = []
    for geoms in component_geoms.values():
        merged = geom_manip.heavy_union(geoms)
        merged_geoms.append(merged)
    print(f"Merged geoms. {len(merged_geoms)}")
    bounds = geom_manip.geom_get_bounds(merged_geoms)
    debug_utils.debug_geoplot_geom(merged_geoms, bounds, "gages_region_map.png")
    print("Plotted gage components")


def create_gage_component_gpkg() -> None:
    gage_components = get_graph_gage_components()
    print(f"Got gage components. {len(gage_components)}")
    component_geoms = {}
    all_wbids = access_utils.all_wbids()
    geoms = gpkg_utils.get_geom_from_wbids_map(all_wbids)
    for gage, components in gage_components.items():
        component_geoms[gage] = [geoms[wbid] for wbid in components if wbid in geoms]
    print(f"Got component geoms. {len(component_geoms)}")
    merged_geoms = []
    size_list = []
    names = []
    for name, geoms in component_geoms.items():
        merged = geom_manip.heavy_union(geoms)
        merged_geoms.append(merged)
        size_list.append(len(geoms))
        names.append(name)
    print(f"Merged geoms. {len(merged_geoms)}")
    bounds = geom_manip.geom_get_bounds(merged_geoms)

    gdf_initial = geopandas.GeoDataFrame(
        {"geometry": merged_geoms, "size": size_list, "names": names},
        crs="EPSG:5070",
        geometry="geometry",
    )
    filename = "gages_region_map.gpkg"
    filename = File_Paths.root_output_dir() / filename
    file_start = time.perf_counter()
    gpkg_utils.create_gpkg(filename)
    gpkg_utils.cleanup_gpkg(filename)
    gpkg_utils.insert_data_gpkg(filename, gdf_initial, "gages_region_map")
    file_end = time.perf_counter()
    print(f"Created gage component geopackage in {file_end-file_start} seconds")
    debug_utils.debug_geoplot_geom(merged_geoms, bounds, "gages_region_map.png")


if __name__ == "__main__":
    print("Hit headerguard of graph_functions.py")
    test_l_ns = False
    test_graph_gage_wbs = False
    test_graph_gage_components = False
    test_create_gage_component_gpkg = True
    if test_l_ns:
        print(get_last_nodes_in_hydrofabric())
    if test_graph_gage_wbs:
        graph_gage_wbs()
    if test_graph_gage_components:
        plot_graph_gage_components()
    if test_create_gage_component_gpkg:
        create_gage_component_gpkg()
