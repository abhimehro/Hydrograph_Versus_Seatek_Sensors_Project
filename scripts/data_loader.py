# scripts/data_loader.py
"""
Load and concatenate data from multiple Excel files in a specified directory.

This function searches for Excel files in the given directory that match the
pattern "RM-*.xlsx". It reads each file into a pandas DataFrame, adds a column
"RM" extracted from the filename, and concatenates all DataFrames into a single
DataFrame.

Args:
    data_dir (str): The directory containing the Excel files to be loaded.

Returns:
    pd.DataFrame: A concatenated DataFrame containing data from all matched Excel files.
"""

import glob
import os

import pandas as pd


def load_data(data_dir):
    all_data = []
    for file in glob.glob(os.path.join(data_dir, "RM-*.xlsx")):
        try:
            df = pd.read_excel(file)
            try:
                rm = float(os.path.basename(file).split("-")[1])
                df["RM"] = rm
            except (ValueError, IndexError):
                print(f"Error extracting RM from filename {file}")
                continue
            all_data.append(df)
        except pd.errors.EmptyDataError as e:
            print(f"Error reading file {file}: {e}")
            continue
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
