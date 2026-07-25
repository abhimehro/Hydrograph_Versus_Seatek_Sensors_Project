import pandas as pd
import numpy as np
import time

def orig_func(df):
    if "Year" not in df.columns or len(df) == 0:
        return None
    if df["Year"].isna().all():
        return None
    years = df["Year"].unique()
    return sorted(years[pd.notna(years)].astype(int).tolist())

def new_func(df):
    if "Year" not in df.columns or len(df) == 0:
        return None
    vals = df["Year"].values
    if len(vals) == 0 or np.all(pd.isna(vals)):
        return None
    years = np.unique(vals[~pd.isna(vals)])
    return sorted(years.astype(int).tolist())

df = pd.DataFrame({'Year': np.random.randint(2010, 2025, 100000)})
df.loc[df.sample(frac=0.1).index, 'Year'] = np.nan

start = time.time()
for _ in range(1000):
    orig_func(df)
print(f"Original: {time.time() - start:.4f}s")

start = time.time()
for _ in range(1000):
    new_func(df)
print(f"New: {time.time() - start:.4f}s")
