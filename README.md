# Hydrograph vs Seatek Sensors Analysis Project

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Table of Contents

- [Introduction](#introduction)
- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Example Visualizations](#example-visualizations)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)

# Seatek Sensor Data Processor

## Introduction

This project processes and visualizes Seatek sensor data alongside hydrograph measurements, providing insights into river bed dynamics and water flow patterns. The system converts raw Seatek readings to NAVD88 elevations and generates professional-grade visualizations for analysis.

## Project Overview

The Hydrograph vs Seatek Sensors Analysis Project combines environmental monitoring data to understand the relationship between water flow (hydrograph) and river bed elevation (Seatek sensors). This tool is essential for:
- Monitoring river bed changes over time
- Analyzing water flow patterns
- Understanding sediment transport dynamics
- Supporting environmental research decisions

## Project Structure

```
Hydrograph_Versus_Seatek_Sensors_Project/
├── src/
│   └── hydrograph_seatek_analysis/      # Main package
│       ├── core/                        # Core functionality
│       │   ├── config.py                # Configuration settings
│       │   └── logger.py                # Logging utilities
│       ├── data/                        # Data processing
│       │   ├── data_loader.py           # Data loading utilities
│       │   ├── processor.py             # Data processing logic
│       │   └── validator.py             # Data validation utilities
│       └── visualization/               # Visualization utilities
│           └── chart_generator.py       # Chart generation
├── data/
│   ├── raw/                             # Raw input data files
│   └── processed/                       # Processed data files
├── output/
│   └── charts/                          # Generated visualizations
├── logs/                                # Processing logs
├── docs/                                # Documentation
├── tests/                               # Test files
├── seatek_processor_new.py              # Main script
├── validate_data.py                     # Data validation script
├── pyproject.toml                       # Poetry configuration
├── setup.py                             # Installation configuration
├── requirements.txt                     # Project dependencies
└── README.md                            # Project documentation
```

## Key Features

- **NAVD88 Conversion**: Accurate conversion of Seatek readings to NAVD88 elevations
- **Time Series Analysis**: Proper handling of temporal data with minute-resolution
- **Dual-axis Visualization**: Professional plots combining Seatek and Hydrograph data
- **Data Validation**: Comprehensive error checking and data quality assurance
- **Automated Processing**: Batch processing of multiple sensors and time periods
- **Detailed Logging**: Comprehensive logging system for tracking processing steps
- **Modular Architecture**: Well-organized code with proper separation of concerns

## Technology Stack

- **Python 3.10+**: Core programming language
- **pandas & numpy**: Data processing and analysis
- **matplotlib & seaborn**: Data visualization
- **openpyxl**: Excel file handling
- **colorlog**: Enhanced logging with color support
- **Poetry**: Dependency management (optional)

## Getting Started

### Prerequisites

```bash
python -m pip install -r requirements.txt
```

### Installation

1. Clone the repository

   ```bash
   git clone https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project.git
   cd Hydrograph_Versus_Seatek_Sensors_Project
   ```
    
2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
   
3. Install the project:

   ```bash
   # Option 1: Install in development mode
   pip install -e .
   
   # Option 2: Install using requirements.txt
   pip install -r requirements.txt
   
   # Option 3: Install using Poetry
   poetry install
   ```

### Usage

1. Place your data files in the appropriate directories:

    - **Raw Data**:
        `data/raw/Data_Summary.xlsx`
        `data/raw/Hydrograph_Seatek_Data.xlsx`

    - **Processed Data**: 
        `data/processed/RM_*.xlsx`

2. Run the processing script:

    ```bash
    # Option 1: Run directly
    python seatek_processor_new.py
    
    # Option 2: If installed as package
    seatek-processor
    ```
   
3. Validate data files:

    ```bash
    # Option 1: Run directly
    python validate_data.py
    
    # Option 2: Run with JSON output
    python validate_data.py --json
    
    # Option 3: Save validation results to file
    python validate_data.py --output validation_results.json
    
    # Option 4: If installed as package
    validate-data
    ```

4. Find generated visualizations in the `output/charts` directory.

## Example Visualizations

The visualization shows:

- Seatek sensor readings (NAVD88) on the left y-axis
- Hydrograph measurements (GPM) on the right y-axis
- Time series in minutes on the x-axis
- Clear correlation between water flow and bed elevation changes

### Sensor 1 Hydrograph Versus Seatek Analysis Visualization

![RM_54 0_Year_1_Sensor 1](https://github.com/user-attachments/assets/de2307b3-68f3-44b3-8b63-2e2bcc8253cf)


### Sensor 2 Hydrograph Versus Seatek Analysis Visualization

![RM_54 0_Year_2_Sensor 1](https://github.com/user-attachments/assets/c351c096-9db8-4c70-94be-dfd9e1f5dc96)

For more of the above visualizations, check the respective directories in the `output/charts/RM_54.0` folder.

## Documentation

- [Installation Guide](docs/technical/installation.md)
- [Data Format Specification](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/blob/main/docs/visualization/data_format.md)
- [API Reference](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/blob/main/docs/visualization/API_Documentation.md)

## Contributing

Contributions are welcome! Please read our [Contributing Guide](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/blob/main/docs/CONTRIBUTING.md) and [Code of Conduct](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/blob/main/docs/CODE_OF_CONDUCT.md).

## License

This project is licensed under the MIT License - see the [License](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/blob/main/docs/LICENSE.md) file for details.

## Contact

- **Author**: Abhi Mehrotra
- **Email**: AbhiMhrtr@pm.me
- **Project Link**: [GitHub Repository](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project)

## Acknowledgments
- LSU Center for River Studies
- Louisiana State University
- The Louisiana Freshwater Sponge Project
- Baton Rouge Community College