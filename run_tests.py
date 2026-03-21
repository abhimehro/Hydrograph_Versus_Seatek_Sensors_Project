import sys
from unittest.mock import MagicMock
sys.modules['pandas'] = MagicMock()
sys.modules['numpy'] = MagicMock()

import pytest
sys.exit(pytest.main(["tests/test_data_processor.py", "test_utils_processor.py"]))
