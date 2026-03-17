## YYYY-MM-DD - [Avoid pd.to_numeric overhead]
**Learning:** `pd.to_numeric(..., errors='coerce')` on an already numeric series creates an unnecessary object copy and performs type checking overhead.
**Action:** Always verify if a column/series is already numeric via `pd.api.types.is_numeric_dtype(series)` before applying `pd.to_numeric` to avoid unnecessary work.
