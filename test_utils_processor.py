import sys
from unittest.mock import MagicMock

# Mock missing dependencies
sys.modules["pandas"] = MagicMock()
sys.modules["numpy"] = MagicMock()

from pathlib import Path

from utils.processor import RiverMileData


def test_river_mile_data_load():
    # Set up mocks
    import pandas as pd

    mock_df = MagicMock()
    mock_df.groupby.return_value = [("2020", MagicMock())]
    mock_df.columns = ["Time (Seconds)", "Year", "Sensor_1"]

    # We need to simulate usecols appending to seen_cols inside read_excel
    def side_effect_read_excel(*args, **kwargs):
        usecols = kwargs.get("usecols")
        if usecols:
            usecols("Time (Seconds)")
            usecols("Year")
            usecols("Sensor_1")
        return mock_df

    pd.read_excel.side_effect = side_effect_read_excel
    pd.read_excel.reset_mock()

    # Test file path
    Path("data/RM_55.xlsx")

    # Mock stat for security check
    p_mock = MagicMock()
    p_mock.stat.return_value.st_size = 1000
    p_mock.stem = "RM_55"
    p_mock.name = "RM_55.xlsx"
    p_mock.exists.return_value = True
    p_mock.is_symlink.return_value = False

    rmd = RiverMileData(p_mock)
    rmd.load_data()

    # Verify pd.read_excel was called with usecols
    pd.read_excel.assert_called_once()
    args, kwargs = pd.read_excel.call_args
    assert "usecols" in kwargs
    assert callable(kwargs["usecols"])


test_river_mile_data_load()
print("test_utils_processor passed!")
