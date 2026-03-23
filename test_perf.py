import sys
from unittest.mock import MagicMock
sys.modules['pandas'] = MagicMock()
sys.modules['numpy'] = MagicMock()
import src.hydrograph_seatek_analysis.data.processor as p
import utils.processor as up
print("Imports successful!")
