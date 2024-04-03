import sys
import os
from pathlib import Path

class File_Paths:
    @staticmethod
    def data_sources() -> Path:
        return Path(__file__).parent.parent / "data"

    @staticmethod
    def root_output_dir() -> Path:
        return Path(__file__).parent.parent / "output"

    @staticmethod
    def template_gpkg() -> Path:
        return File_Paths.data_sources() / "template.gpkg"

    @staticmethod
    def conus_hydrofabric() -> Path:
        return File_Paths.data_sources() / "conus.gpkg"

    @staticmethod
    def hydrofabric_graph() -> Path:
        return File_Paths.conus_hydrofabric().with_suffix(".gpickle")
