from unittest.mock import MagicMock, patch
import sys
sys.modules['pandas'] = MagicMock()
sys.modules['numpy'] = MagicMock()

from utils.processor import RiverMileData
from pathlib import Path

p = Path("data/RM_55.xlsx")
p_mock = MagicMock()
p_mock.stat.return_value.st_size = 1000
p_mock.stem = "RM_55"
p_mock.name = "RM_55.xlsx"
p_mock.exists.return_value = True

rmd = RiverMileData(p_mock)
with patch('utils.processor.pd.read_excel') as mock_read_excel:
    mock_df = MagicMock()
    mock_df.groupby.return_value = [("2020", MagicMock())]
    mock_df.columns = ["Time (Seconds)", "Year", "Sensor_1"]
    def side_effect_read_excel(*args, **kwargs):
        usecols = kwargs.get('usecols')
        if usecols:
            usecols('Time (Seconds)')
            usecols('Year')
            usecols('Sensor_1')
        return mock_df
    mock_read_excel.side_effect = side_effect_read_excel
    rmd.load_data()
    print("Call count:", mock_read_excel.call_count)
