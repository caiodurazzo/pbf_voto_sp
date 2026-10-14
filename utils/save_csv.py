import os
import pandas as pd
from config import data_folder

def save_csv(df: pd.DataFrame, file_name):
    
    if not os.path.exists(data_folder):

        os.makedirs(data_folder)
    
    file_path = os.path.join(data_folder, file_name)
    
    df.to_csv(file_path, index = False)

    print(f'Base salva em {file_path}')