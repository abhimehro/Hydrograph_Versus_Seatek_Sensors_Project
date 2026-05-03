import pandas as pd
import numpy as np
df = pd.DataFrame({'Year': [2020.0, 2021.0, np.nan, 2020.0]})
years = df["Year"].unique()
valid_years = years[pd.notna(years)]
print(sorted(valid_years.astype(int).tolist()))
