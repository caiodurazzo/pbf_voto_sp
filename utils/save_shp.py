import os
import geopandas as gpd
from config import data_folder

def save_shp(gdf: gpd.GeoDataFrame, file_name: str = "data.shp"):
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    file_path = os.path.join(data_folder, file_name)

    gdf.to_file(file_path)

    print(f"Shapefile salvo em {file_path}")