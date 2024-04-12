from file_utils import File_Paths
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
import time

# Convert the last_nodes.txt file to a markdown file

def list_to_md_list(lst):
    return "\n" + "\n".join([f"- {item}" for item in lst]) + "\n"

def to_md_list_file(lst, file):
    md = list_to_md_list(lst)
    with open(file, "w") as f:
        #Header
        f.write("# Last Nodes\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%B %d, %Y')}\n")
        f.write(f"Using script: {os.path.basename(__file__)}\n")
        f.write(md)

def last_nodes_to_md():
    with open(File_Paths.root_output_dir() / "last_nodes.txt", "r") as f:
        last_nodes = f.read().split("\n")
    to_md_list_file(last_nodes, File_Paths.root_output_dir() / "last_nodes.md")

if __name__ == "__main__":
    last_nodes_to_md()