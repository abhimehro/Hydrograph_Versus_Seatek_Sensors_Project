#!/usr/bin/env python3

"""
Seatek Sensor and Hydrograph Data Visualization
---------------------------------------------
Description: Processes and visualizes Seatek sensor data with hydrograph measurements.
Converts Seatek readings to NAVD88 elevations and creates professional visualizations.

Key Features:
- NAVD88 conversion with river mile-specific offsets
- Proper time axis in minutes
- Dual-axis visualization for Seatek and Hydrograph data
- Professional styling and formatting
- Comprehensive error handling and logging

Author: Abhi Mehrotra
Date: March 2025
Version: 3.0.0
"""

import sys
from src.hydrograph_seatek_analysis.app import main

if __name__ == "__main__":
    sys.exit(main())