import matplotlib.pyplot as plt
from config import graphs_folder
import os

def save_graph(fig,
               file_name: str,
               dpi: int = 300,
               bbox_inches: str = "tight") -> None:
    
    if not os.path.exists(graphs_folder):
        os.makedirs(graphs_folder)

    file_name = os.path.join(graphs_folder, file_name)

    if not file_name.endswith(".png"):
        file_name += ".png"
    
    fig.savefig(file_name, dpi = dpi, bbox_inches = bbox_inches)