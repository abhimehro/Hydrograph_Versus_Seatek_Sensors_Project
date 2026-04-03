import time

import numpy as np
import pandas as pd

# Create dummy data
n = 1_000_000
data = np.random.randn(n)
data[np.random.choice(n, 10000, replace=False)] = np.nan
data[np.random.choice(n, 10000, replace=False)] = 0
s = pd.Series(data)

# Method 1
start = time.time()
for _ in range(100):
    sensor_isna = s.isna()
    sensor_iszero = s == 0
    nulls = sensor_isna.sum()
    zeros = sensor_iszero.sum()
    vals = s.values
    mask1 = ~pd.isna(vals) & (vals != 0)
time1 = time.time() - start

# Method 2
start = time.time()
for _ in range(100):
    sensor_isna = s.isna()
    sensor_iszero = s == 0
    nulls = sensor_isna.sum()
    zeros = sensor_iszero.sum()
    mask2 = ~(sensor_isna.values | sensor_iszero.values)
time2 = time.time() - start

print(f"Method 1: {time1:.4f}s")
print(f"Method 2: {time2:.4f}s")
print(f"Same? {np.array_equal(mask1, mask2)}")
