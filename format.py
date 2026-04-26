def format_file(filepath):
    """
    Reads a file and applies various formatting fixes, including fixing long lines
    and ensuring proper module usage.
    """
    with open(filepath, 'r') as f:
        content = f.read()

    # Remove trailing spaces
    content = '\n'.join([line.rstrip() for line in content.split('\n')])

    # Replace the numpy/pandas inline imports with proper module usage
    content = content.replace("__import__('pandas').Series", "pd.Series")
    content = content.replace("__import__('pandas').DataFrame", "pd.DataFrame")
    content = content.replace("__import__('numpy').nan", "np.nan")

    # Fix some of the obvious line length issues by adding continuations.
    # We use parentheses for multiline continuation as it's cleaner than backslashes.

    # 1. Fix sensor_keep assignment (without existing parentheses)
    content = content.replace(
        "merged.loc[~sensor_keep, sensor] = pd.NA if pd.api.types.is_object_dtype(merged[sensor]) else np.nan",
        ("merged.loc[~sensor_keep, sensor] = (\n"
         "                        pd.NA if pd.api.types.is_object_dtype(merged[sensor]) else np.nan\n"
         "                    )")
    )
    # 2. Fix sensor_keep assignment (with existing single-line parentheses)
    content = content.replace(
        "merged.loc[~sensor_keep, sensor] = (pd.NA if pd.api.types.is_object_dtype(merged[sensor]) else np.nan)",
        ("merged.loc[~sensor_keep, sensor] = (\n"
         "                        pd.NA if pd.api.types.is_object_dtype(merged[sensor]) else np.nan\n"
         "                    )")
    )

    # 3. Fix hydro_keep assignment (without existing parentheses)
    content = content.replace(
        "merged.loc[~hydro_keep, 'Hydrograph (Lagged)'] = pd.NA if pd.api.types.is_object_dtype(merged['Hydrograph (Lagged)']) else np.nan",
        ("merged.loc[~hydro_keep, 'Hydrograph (Lagged)'] = (\n"
         "                        pd.NA if pd.api.types.is_object_dtype(merged['Hydrograph (Lagged)']) else np.nan\n"
         "                    )")
    )
    # 4. Fix hydro_keep assignment (with existing single-line parentheses)
    content = content.replace(
        "merged.loc[~hydro_keep, 'Hydrograph (Lagged)'] = (pd.NA if pd.api.types.is_object_dtype(merged['Hydrograph (Lagged)']) else np.nan)",
        ("merged.loc[~hydro_keep, 'Hydrograph (Lagged)'] = (\n"
         "                        pd.NA if pd.api.types.is_object_dtype(merged['Hydrograph (Lagged)']) else np.nan\n"
         "                    )")
    )

    # 5. Fix long logger.info call in utils/processor.py
    content = content.replace(
        "logger.info(f'Data processing metrics:\\n  Original rows: {self.original_rows}\\n  Invalid rows: {self.invalid_rows}\\n  Zero values: {self.zero_values}\\n  Null values: {self.null_values}\\n  Valid rows: {self.valid_rows}')",
        ("logger.info(\n"
         "            \"Data processing metrics:\\n\"\n"
         "            f\"  Original rows: {self.original_rows}\\n\"\n"
         "            f\"  Invalid rows: {self.invalid_rows}\\n\"\n"
         "            f\"  Zero values: {self.zero_values}\\n\"\n"
         "            f\"  Null values: {self.null_values}\\n\"\n"
         "            f\"  Valid rows: {self.valid_rows}\"\n"
         "        )")
    )

    # 6. Fix long ValueError for file size in data_loader.py and processor.py
    content = content.replace(
        "raise ValueError(f\"File size exceeds maximum allowed size ({self.config.max_file_size_bytes} bytes): {summary_file}\")",
        ("raise ValueError(\n"
         "                    f\"File size exceeds maximum allowed size ({self.config.max_file_size_bytes} bytes): \"\n"
         "                    f\"{summary_file}\"\n"
         "                )")
    )
    content = content.replace(
        "raise ValueError(f\"File size exceeds maximum allowed size ({self.config.max_file_size_bytes} bytes): {hydro_file}\")",
        ("raise ValueError(\n"
         "                    f\"File size exceeds maximum allowed size ({self.config.max_file_size_bytes} bytes): \"\n"
         "                    f\"{hydro_file}\"\n"
         "                )")
    )
    content = content.replace(
        "raise ValueError(f\"File size exceeds maximum allowed size ({max_file_size_bytes} bytes): {self.file_path}\")",
        ("raise ValueError(\n"
         "                f\"File size exceeds maximum allowed size ({max_file_size_bytes} bytes): \"\n"
         "                f\"{self.file_path}\"\n"
         "            )")
    )

    # 7. Fix long logger.error for file size in validator.py
    content = content.replace(
        "logger.error(f\"Summary file size exceeds maximum allowed size ({self.config.max_file_size_bytes} bytes): {summary_file}\")",
        ("logger.error(\n"
         "                f\"Summary file size exceeds maximum allowed size ({self.config.max_file_size_bytes} bytes): \"\n"
         "                f\"{summary_file}\"\n"
         "            )")
    )
    content = content.replace(
        "logger.error(f\"Hydrograph file size exceeds maximum allowed size ({self.config.max_file_size_bytes} bytes): {hydro_file}\")",
        ("logger.error(\n"
         "                f\"Hydrograph file size exceeds maximum allowed size ({self.config.max_file_size_bytes} bytes): \"\n"
         "                f\"{hydro_file}\"\n"
         "            )")
    )
    content = content.replace(
        "logger.error(f\"Processed file size exceeds maximum allowed size ({self.config.max_file_size_bytes} bytes): {file_path}\")",
        ("logger.error(\n"
         "                    f\"Processed file size exceeds maximum allowed size ({self.config.max_file_size_bytes} bytes): \"\n"
         "                    f\"{file_path}\"\n"
         "                )")
    )

    if not content.endswith('\n'):
        content += '\n'

    with open(filepath, 'w') as f:
        f.write(content)


if __name__ == "__main__":
    target_files = [
        'src/hydrograph_seatek_analysis/data/processor.py',
        'src/hydrograph_seatek_analysis/data/data_loader.py',
        'src/hydrograph_seatek_analysis/data/validator.py',
        'utils/processor.py'
    ]

    for filepath in target_files:
        format_file(filepath)

        # Ensure numpy is imported if used
        with open(filepath, 'r') as f:
            file_content = f.read()

        if 'import numpy as np' not in file_content and 'np.' in file_content:
            if 'import pandas as pd' in file_content:
                file_content = file_content.replace(
                    'import pandas as pd',
                    'import pandas as pd\nimport numpy as np'
                )
            else:
                # Fallback: add to the top if pandas import not found
                file_content = 'import numpy as np\n' + file_content

            with open(filepath, 'w') as f:
                f.write(file_content)
