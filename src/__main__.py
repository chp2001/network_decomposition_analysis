from file_utils import File_Paths
import cli_graph_utils as graph_utils
import cli_access_utils as access_utils
from graph_functions import get_last_nodes_in_hydrofabric


import os
import sys
from datetime import datetime
from pathlib import Path

import time

# Interface file

arg_options = {  # name, description
    "-h": "Prints the help message",
    "-l_ns": "Gets a list of the last nodes in the hydrofabric for non-terminating subgraphs. No config file needed, overrides need for first positional argument",
}

supported_filetypes = {
    ".csv": "comma separated values",
    ".txt": "plaintext, newline separated values",
    "": "plaintext, newline separated values",
}

default_forcing_config = {
    "start_time": "2010-01-01, 12:00 AM",
    "end_time": "2010-01-02, 12:00 AM",
}

for t in ["start_time", "end_time"]:
    # print(f"Converting {default_forcing_config[time]} to datetime")
    default_forcing_config[t] = datetime.strptime(
        default_forcing_config[t], "%Y-%m-%d, %I:%M %p"
    )
    default_forcing_config[t] = datetime.strftime(
        default_forcing_config[t], "%Y-%m-%dT%H:%M"
    )
    # print(f"Converted {default_forcing_config[time]} to datetime")


def print_help():
    print("This is the help message for the command line interface")
    for key in arg_options:
        print(f"{key}: {arg_options[key]}")


def get_input_wbs():
    if len(sys.argv) < 2:
        raise Exception("No file path given")
    path = Path(sys.argv[1])
    if not path.exists():
        raise Exception(f"File {path} does not exist")
    filename = path.name
    filetype = None
    if not path.is_file():
        raise Exception(f"Path {path} is not a file")
    ext = path.suffix
    if not "." in filename:
        filetype = "plaintext"
    else:
        filetype = ext
    if filetype not in supported_filetypes:
        raise Exception(f"Filetype {filetype} not supported")
    return path, filetype


def read_input_wbs(path, filetype):
    if filetype == ".csv":
        with open(path, "r") as f:
            return f.read().split(",")
    elif filetype == ".txt" or filetype == "":
        with open(path, "r") as f:
            return f.read().split("\n")
    else:
        raise Exception(f"Filetype {filetype} not supported")


def get_output_foldername(ids):
    # upstream_ids = graph_utils.get_upstream_ids(ids)
    return ids[0]


def main():
    if "-h" in sys.argv:
        print_help()
        return
    if "-l_ns" in sys.argv or True:
        last_nodes = get_last_nodes_in_hydrofabric()
        with open(File_Paths.root_output_dir() / "last_nodes.txt", "w") as f:
            f.write("\n".join(last_nodes))
        return
    print("No arguments given, exiting...")
    return


if __name__ == "__main__":
    main()
