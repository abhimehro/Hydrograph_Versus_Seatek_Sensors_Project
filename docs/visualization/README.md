# Hydrograph vs Seatek Sensors Project

![GitHub issues](https://img.shields.io/github/issues/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

## Overview
This project analyzes and visualizes Seatek sensor data collected from various river miles over a 20-year period (1995-2014). The project processes data from Excel files containing sensor readings and generates comprehensive visualizations to help understand temporal patterns and variations in sensor measurements.

## Quick Navigation
- [Installation Guide](docs/installation.md)
- [Sensor Analysis Documentation](docs/sensor_analysis.md)
- [Data Format Specification](docs/data_format.md)
- [Visualization Guide](docs/visualization_guide.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## Project Structure
```
Hydrograph_Versus_Seatek_Sensors_Project/
├── src/                      # Source code
│   └── sensor-visualization.py
├── data/                     # Data files
│   ├── raw/                 
│   └── processed/           
├── output/                   # Generated visualizations
│   └── RM_*/                # River mile outputs
│       └── sensor_charts/    # Sensor analysis outputs
├── docs/                     # Documentation
│   ├── installation.md
│   ├── sensor_analysis.md
│   ├── data_format.md
│   └── visualization_guide.md
├── tests/                    # Unit tests
├── requirements.txt          # Core dependencies
└── requirements-dev.txt      # Development dependencies
```

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project.git
   cd Hydrograph_Versus_Seatek_Sensors_Project
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run Analysis**
   ```bash
   python src/sensor-visualization.py
   ```

3. **View Results**
   - Check `output/` directory for generated visualizations
   - Each river mile has its own subdirectory with sensor-specific analysis

## Key Features
- Multi-sensor time series analysis
- Statistical insights and trend analysis
- Professional-grade visualizations
- Automated data validation and processing
- Configurable output formats

## Core Dependencies
- Python ≥ 3.9
- pandas ≥ 2.2.3
- matplotlib ≥ 3.7.3
- numpy ≥ 2.2.0
- seaborn ≥ 0.13.0

## License
This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Contact & Support
- **Author**: Abhi Mehrotra
- **Email**: abhimhrtr@pm.com
- **Issues**: [GitHub Issues](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/issues)
