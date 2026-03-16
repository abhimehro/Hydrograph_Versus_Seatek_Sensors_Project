import sys
from unittest.mock import MagicMock, ANY

# Mock missing dependencies
sys.modules['pandas'] = MagicMock()
sys.modules['numpy'] = MagicMock()

from utils.data_loader import DataLoader
from utils.config import Config
from pathlib import Path

def test_data_loader():
    import pandas as pd

    mock_summary_df = MagicMock()
    mock_summary_df.columns = ['River_Mile', 'Y_Offset', 'Num_Sensors']

    def side_effect_read_excel(*args, **kwargs):
        usecols = kwargs.get('usecols')
        if usecols:
            if 'Data_Summary' in str(args[0]):
                usecols('River_Mile')
                usecols('Y_Offset')
                usecols('Num_Sensors')
            elif 'sheet_name' in kwargs:
                usecols('Time (Seconds)')
                usecols('Year')
                usecols('Sensor_1')
                usecols('Hydrograph (Lagged)')
        return mock_summary_df

    pd.read_excel.side_effect = side_effect_read_excel

    # Mock ExcelFile
    mock_excel_file = MagicMock()
    mock_excel_file.sheet_names = ['RM_55']
    pd.ExcelFile.return_value = mock_excel_file

    # Mock Config to avoid permission errors
    config = MagicMock()
    config.max_file_size_bytes = 100000000

    # Mock files
    config.summary_file = MagicMock()
    config.summary_file.exists.return_value = True
    config.summary_file.stat.return_value.st_size = 1000
    config.summary_file.__str__.return_value = "Data_Summary.xlsx"

    config.hydro_file = MagicMock()
    config.hydro_file.exists.return_value = True
    config.hydro_file.stat.return_value.st_size = 1000
    config.hydro_file.__str__.return_value = "Hydrograph_Seatek_Data.xlsx"

    loader = DataLoader(config)
    loader.load_all_data()

    assert pd.read_excel.call_count == 2

test_data_loader()
print("test_utils_data_loader passed!")
