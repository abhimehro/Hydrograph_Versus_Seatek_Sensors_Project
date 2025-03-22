# Installation Guide

This guide provides detailed instructions for installing and setting up the Hydrograph vs Seatek Sensors Analysis Project.

## System Requirements

### Hardware Requirements
```
- CPU: Multi-core processor recommended
- RAM: 8GB minimum, 16GB recommended
- Storage: 1GB free space minimum
- GPU: Optional - for accelerated visualization
```

### Software Requirements
```
- Python 3.10 or higher
- Operating System: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)
- Additional tools: git, virtualenv or venv
```

## Installation Methods

You can install the project using one of the following methods:

### Method 1: Direct Installation (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project.git
   cd Hydrograph_Versus_Seatek_Sensors_Project
   ```

2. Create and activate a virtual environment:
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install the project in development mode:
   ```bash
   pip install -e .
   ```

   This will install the project and its dependencies, and also make the command-line tools available.

### Method 2: Using pip with requirements.txt

1. Clone the repository:
   ```bash
   git clone https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project.git
   cd Hydrograph_Versus_Seatek_Sensors_Project
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies from requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

### Method 3: Using Poetry

[Poetry](https://python-poetry.org/) is a modern Python package and dependency manager.

1. Install Poetry if you don't have it:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project.git
   cd Hydrograph_Versus_Seatek_Sensors_Project
   ```

3. Install the project and its dependencies:
   ```bash
   poetry install
   ```

4. Activate the Poetry shell:
   ```bash
   poetry shell
   ```

## Verifying Installation

After installation, you can verify that everything is set up correctly:

### Check Command-Line Tools

If you installed the project with `pip install -e .` or Poetry, you should have access to the command-line tools:

```bash
# Check if the data validator is available
validate-data --help

# Check if the Seatek processor is available
seatek-processor --help
```

### Run the Data Validation Script

```bash
python validate_data.py
```

If the installation was successful, you should see the validation results for your data files.

## Setting Up Data Directories

The project expects data to be organized in a specific directory structure:

```
Hydrograph_Versus_Seatek_Sensors_Project/
├── data/
│   ├── raw/                    # Raw input data files
│   │   ├── Data_Summary.xlsx   # Summary data
│   │   └── Hydrograph_Seatek_Data.xlsx  # Hydrograph data
│   └── processed/              # Processed data files
│       ├── RM_54.0.xlsx        # River mile data
│       ├── RM_53.0.xlsx
│       └── ...
├── output/
│   └── charts/                 # Generated visualizations
└── logs/                       # Processing logs
```

You can create these directories manually or run the following command:

```bash
mkdir -p data/raw data/processed output/charts logs
```

## Environment Variables

The project supports the following environment variables:

- `HYDROGRAPH_BASE_DIR`: Override the base directory for data files. By default, the current working directory is used.

Example:
```bash
# Set the base directory to a specific path
export HYDROGRAPH_BASE_DIR=/path/to/data

# Run the processor with the custom base directory
seatek-processor
```

## Development Setup

If you plan to develop or modify the project, you'll need additional tools:

### Install Development Dependencies

```bash
# Using pip
pip install pytest pytest-cov black flake8 mypy pre-commit

# Using Poetry
poetry install --with dev
```

### Set Up Pre-commit Hooks

The project uses [pre-commit](https://pre-commit.com/) to ensure code quality:

```bash
pre-commit install
```

This will install Git hooks that run checks before each commit.

### Run Tests

```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=src

# Run specific test modules
python -m pytest tests/test_config.py
```

## Memory and Performance Optimization

The project includes several performance optimizations:

### Memory Management

```python
# Configure memory optimization settings
import pandas as pd

# Optimize Pandas settings
pd.options.mode.chained_assignment = None
pd.options.display.max_rows = 100
```

### Multiprocessing Potential

The current implementation is sequential, but the architecture supports potential parallelization:

- Processing different river miles could be parallelized
- Processing different years/sensors could be parallelized
- Chart generation could be parallelized

## Troubleshooting

### Missing Dependencies

If you encounter errors about missing packages, ensure you've installed all dependencies:

```bash
pip install -r requirements.txt
```

### File Not Found Errors

If you see errors about missing data files, check that you've placed the required data files in the correct directories:

- `data/raw/Data_Summary.xlsx`
- `data/raw/Hydrograph_Seatek_Data.xlsx`
- `data/processed/RM_*.xlsx`

### Matplotlib/Visualization Issues

If you encounter issues with matplotlib or visualization:

1. Check that you have a functioning backend:
   ```bash
   python -c "import matplotlib.pyplot as plt; plt.figure(); plt.close()"
   ```

2. If running on a headless server, you may need to use a non-interactive backend:
   ```python
   import matplotlib
   matplotlib.use('Agg')  # Use non-interactive backend
   import matplotlib.pyplot as plt
   ```

### Python Version Issues

The project requires Python 3.10 or higher. Check your Python version:

```bash
python --version
```

If you're using an older version, consider using [pyenv](https://github.com/pyenv/pyenv) to manage multiple Python versions.

### Virtual Environment Issues

If you're having issues with the virtual environment:

```python
# Verify if running in a virtual environment
import sys
in_venv = hasattr(sys, 'real_prefix') or sys.base_prefix != sys.prefix
print(f"Running in virtual environment: {in_venv}")
```

### Permission Issues

Check for required permissions:

```python
import os
paths = ['data', 'output', 'logs']
for path in paths:
    has_write_access = os.access(path, os.W_OK)
    print(f"Write access to {path}: {has_write_access}")
```

## Maintenance

### Regular Updates

Keep your dependencies up to date:

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Using Poetry
poetry update
```

### Log Rotation

The application automatically sets up log rotation:

```python
handler = logging.handlers.RotatingFileHandler(
    'logs/sensor_visualization.log',
    maxBytes=10_000_000,  # 10MB
    backupCount=5
)
```

## Security Considerations

### Data Directory Permissions

Ensure proper permissions for data directories:

```python
import os
import stat

dirs = ['data/raw', 'data/processed']
for dir_path in dirs:
    os.chmod(dir_path, stat.S_IRUSR | stat.S_IWUSR)
```

## Getting Help

If you encounter any issues not covered in this guide, please:

1. Check the project documentation in the `docs/` directory
2. File an issue on the [GitHub repository](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/issues)
3. Contact the maintainer at AbhiMhrtr@pm.me