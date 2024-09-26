# Hydrograph-Versus-Seatek-Sensors-Project

This project analyzes and visualizes data from Seatek sensors in relation to hydrograph measurements across various River Miles (RMs) along a river system.

## Project Overview

The project processes data for multiple River Miles, each with a varying number of sensors, and generates charts comparing sensor data with hydrograph measurements over a 20-year period.

## Project Structure

Hydrograph-Versus-Seatek-Sensors-Project/
├── data/
│   ├── raw/ # Original Excel files
│   └── processed/ # Processed CSV files
├── scripts/ # Python scripts for data processing and analysis
├── charts/ # Generated chart images
├── docs/ # Project documentation
└── tests/ # Unit tests


## Setup

1. Clone the repository:

```bash
git clone https://github.com/abhimehro/Hydrograph-Versus-Seatek-Sensors-Project.git
cd Hydrograph-Versus-Seatek-Sensors-Project
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate # On Windows use venv\Scripts\activate.bat
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Place raw data files in the `data/raw/` directory.
2. Run data processing script:

```bash
python scripts/process_data.py
```

3. View generated charts in the `charts/` directory.

## Configuration

Edit the `config.yaml` file to adjust settings such as River Miles, sensor configurations, and chart parameters.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contact

Abhi Mehrotra - <abhimehrotra@outlook.com>

Project Link: [https://github.com/abhimehro/Hydrograph-Versus-Seatek-Sensors-Project](https://github.com/abhimehro/Hydrograph-Versus-Seatek-Sensors-Project)
