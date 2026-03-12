import re

def format_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Remove trailing spaces
    content = '\n'.join([line.rstrip() for line in content.split('\n')])

    # Replace the numpy/pandas inline imports with proper module usage
    content = content.replace("__import__('pandas').Series", "pd.Series")
    content = content.replace("__import__('pandas').DataFrame", "pd.DataFrame")
    content = content.replace("__import__('numpy').nan", "np.nan")

    # Fix some of the obvious line length issues by adding continuations
    content = content.replace("merged.loc[~sensor_keep, sensor] = pd.NA if pd.api.types.is_object_dtype(merged[sensor]) else np.nan",
                              "merged.loc[~sensor_keep, sensor] = (\\n                        pd.NA if pd.api.types.is_object_dtype(merged[sensor]) else np.nan\\n                    )")
    content = content.replace("merged.loc[~hydro_keep, 'Hydrograph (Lagged)'] = pd.NA if pd.api.types.is_object_dtype(merged['Hydrograph (Lagged)']) else np.nan",
                              "merged.loc[~hydro_keep, 'Hydrograph (Lagged)'] = (\\n                        pd.NA if pd.api.types.is_object_dtype(merged['Hydrograph (Lagged)']) else np.nan\\n                    )")

    if not content.endswith('\n'):
        content += '\n'

    with open(filepath, 'w') as f:
        f.write(content)

format_file('src/hydrograph_seatek_analysis/data/processor.py')
format_file('utils/processor.py')

with open('src/hydrograph_seatek_analysis/data/processor.py', 'r') as f:
    if 'import numpy as np' not in f.read():
        with open('src/hydrograph_seatek_analysis/data/processor.py', 'r') as f2:
            content = f2.read()
            content = content.replace('import pandas as pd', 'import pandas as pd\nimport numpy as np')
        with open('src/hydrograph_seatek_analysis/data/processor.py', 'w') as f2:
            f2.write(content)

with open('utils/processor.py', 'r') as f:
    if 'import numpy as np' not in f.read():
        with open('utils/processor.py', 'r') as f2:
            content = f2.read()
            content = content.replace('import pandas as pd', 'import pandas as pd\nimport numpy as np')
        with open('utils/processor.py', 'w') as f2:
            f2.write(content)
