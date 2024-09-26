# Hydrograph-Versus-Seatek-Sensors-Project

This project analyzes and visualizes data from Seatek sensors in relation to hydrograph measurements across various River Miles (RMs) along a river system.

## Project Overview

The project processes data for multiple River Miles, each with a varying number of sensors, and generates charts comparing sensor data with hydrograph measurements over a 20-year period.

## Project Structure

Hydrograph-Versus-Seatek-Sensors-Project/
├── data/
│ ├── raw/ # Original Excel files
│ └── processed/ # Processed CSV files
├── scripts/
│ ├── main.py
│ ├── data_loader.py
│ ├── data_processor.py
│ └── visualizer.py
├── output/
│ └── charts/ # Generated chart images
├── tests/
│ └── test_data_processor.py
├── docs/
├── .gitignore
├── README.md
├── requirements.txt
└── config.yaml

## Setup

1. Clone the repository:

```bash
git clone https://github.com/abhimehro/Hydrograph-Versus-Seatek-Sensors-Project.git
cd Hydrograph-Versus-Seatek-Sensors-Project
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate # On Windows use venv\Scripts\activate.bat
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Place raw Excel files in the `data/raw/` directory.

2. Run the main script:

```bash
python scripts/main.py
```

3. View processed data in `data/processed/` and generated charts in `output/charts/`.

## Running Tests

To run the unit tests:

## Configuration

Edit the `config.yaml` file to adjust settings such as data directory paths, River Miles, sensor configurations, and chart parameters.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contact

Abhi Mehrotra - <abhimehrotra@outlook.com>

Project Link: [https://github.com/abhimehro/Hydrograph-Versus-Seatek-Sensors-Project](https://github.com/abhimehro/Hydrograph-Versus-Seatek-Sensors-Project)
