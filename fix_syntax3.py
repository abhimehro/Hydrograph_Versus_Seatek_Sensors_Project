import sys

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    content = content.replace("(\n                        pd.NA if pd.api.types.is_object_dtype(merged[sensor]) else np.nan\n                    )", "(pd.NA if pd.api.types.is_object_dtype(merged[sensor]) else np.nan)")
    content = content.replace("(\n                        pd.NA if pd.api.types.is_object_dtype(merged['Hydrograph (Lagged)']) else np.nan\n                    )", "(pd.NA if pd.api.types.is_object_dtype(merged['Hydrograph (Lagged)']) else np.nan)")
    content = content.replace("(\\n                        pd.NA if pd.api.types.is_object_dtype(merged[sensor]) else np.nan\n                    )", "(pd.NA if pd.api.types.is_object_dtype(merged[sensor]) else np.nan)")
    content = content.replace("(\\n                        pd.NA if pd.api.types.is_object_dtype(merged['Hydrograph (Lagged)']) else np.nan\n                    )", "(pd.NA if pd.api.types.is_object_dtype(merged['Hydrograph (Lagged)']) else np.nan)")

    with open(filepath, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    fix_file('src/hydrograph_seatek_analysis/data/processor.py')
    fix_file('utils/processor.py')
