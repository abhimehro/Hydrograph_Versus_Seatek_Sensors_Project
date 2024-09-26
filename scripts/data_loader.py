# scripts/data_loader.py

import pandas as pd
import glob
import os

def load_data(data_dir):
    all_data = []
    for file in glob.glob(os.path.join(data_dir, "RM-*.xlsx")):
        df = pd.read_excel(file, header=1)
        rm = float(os.path.basename(file).split("-")[1])
        df['RM'] = rm
        all_data.append(df)
    return pd.concat(all_data, ignore_index=True)