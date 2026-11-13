import os
import pandas as pd
from config import data_folder

def load_csv(file_name: str, **read_kwargs) -> pd.DataFrame:

    file_path = os.path.join(data_folder, file_name)

    if not os.path.exists(file_path):

        raise FileNotFoundError(f'O arquivo {file_name} não existe em data_folder')
    
    return pd.read_csv(file_path, **read_kwargs)