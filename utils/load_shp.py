import os
import geopandas as gpd
from config import data_folder

def load_shp(file_name: str = "data.shp", **read_kwargs) -> gpd.GeoDataFrame:

    file_path = os.path.join(data_folder, file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"O .shp {file_name} não existe em {os.path.join(data_folder)}")
    
    return gpd.read_file(file_path, **read_kwargs)