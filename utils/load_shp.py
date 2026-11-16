import os
import geopandas as gpd

from typing import cast
from config import data_folder


def load_shp(file_name: str = "data.shp", **read_kwargs) -> gpd.GeoDataFrame:

    file_path = os.path.join(data_folder, file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    return cast(gpd.GeoDataFrame, gpd.read_file(file_path, **read_kwargs))