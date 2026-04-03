import timeit

import numpy as np
import pandas as pd

n = 1000000
df = pd.DataFrame(
    {
        "Sensor": np.random.choice([0, 1, np.nan], size=n, p=[0.1, 0.8, 0.1]),
        "Hydrograph": np.random.choice([0, 1, np.nan], size=n, p=[0.1, 0.8, 0.1]),
    }
)


def original_way():
    sensor_mask = df["Sensor"].notna() & (df["Sensor"] != 0)
    hydro_mask = df["Hydrograph"].notna() & (df["Hydrograph"] != 0)
    return sensor_mask, hydro_mask


def optimized_way():
    # Cache underlying numpy arrays to avoid repeated pandas Series indexing overhead
    sensor_vals = df["Sensor"].values
    sensor_mask = ~np.isnan(sensor_vals) & (sensor_vals != 0)

    hydro_vals = df["Hydrograph"].values
    hydro_mask = ~np.isnan(hydro_vals) & (hydro_vals != 0)

    return pd.Series(sensor_mask, index=df.index), pd.Series(hydro_mask, index=df.index)


print("Original pandas logic:", timeit.timeit(original_way, number=100))
print("Optimized numpy logic:", timeit.timeit(optimized_way, number=100))
