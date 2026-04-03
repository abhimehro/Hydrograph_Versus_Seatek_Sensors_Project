def fix_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    content = content.replace(
        "pd.NA if pd.api.types.is_object_dtype(merged[sensor]) else np.nan\\n",
        "pd.NA if pd.api.types.is_object_dtype(merged[sensor]) else np.nan\n",
    )
    content = content.replace(
        "pd.NA if pd.api.types.is_object_dtype(merged['Hydrograph (Lagged)']) else np.nan\\n",
        "pd.NA if pd.api.types.is_object_dtype(merged['Hydrograph (Lagged)']) else np.nan\n",
    )

    # Just replace that whole block to be safe
    old1 = "merged.loc[~sensor_keep, sensor] = (\\n                        pd.NA if pd.api.types.is_object_dtype(merged[sensor]) else np.nan\\n                    )"
    new1 = "merged.loc[~sensor_keep, sensor] = (pd.NA if pd.api.types.is_object_dtype(merged[sensor]) else np.nan)"
    content = content.replace(old1, new1)

    old2 = "merged.loc[~hydro_keep, 'Hydrograph (Lagged)'] = (\\n                        pd.NA if pd.api.types.is_object_dtype(merged['Hydrograph (Lagged)']) else np.nan\\n                    )"
    new2 = "merged.loc[~hydro_keep, 'Hydrograph (Lagged)'] = (pd.NA if pd.api.types.is_object_dtype(merged['Hydrograph (Lagged)']) else np.nan)"
    content = content.replace(old2, new2)

    with open(filepath, "w") as f:
        f.write(content)


if __name__ == "__main__":
    fix_file("src/hydrograph_seatek_analysis/data/processor.py")
    fix_file("utils/processor.py")
