# Hydrograph-Versus-Seatek-Sensors-Project

[![GitHub issues](https://img.shields.io/github/issues/abhimehro/Hydrograph-Versus-Seatek-Sensors-Project)](https://github.com/abhimehro/Hydrograph-Versus-Seatek-Sensors-Project/issues)

This project aims to visualize and analyze Seatek sensor data against hydrograph data for different river miles and years.

## Project Overview:

The project consists of one main component:

1. **Visualizer**: Creates visualizations to compare sensor data with hydrograph measurements.
   The project processes data for multiple River Miles, each with a varying number of sensors, and generates charts comparing sensor data with hydrograph measurements over a 20-year period.

## Project Structure:

Hydrograph-Versus-Seatek-Sensors-Project/ ├── data/ │ ├── Hydrograph_Seatek_Data.xlsx │ ├── Data_Summary.csv ├── scripts/ │ ├── visualizer.py │ ├── main.py ├── output/ │ ├── charts/ ├── docs/ │ ├── README.md

## Data:

The raw data is stored in the `data` folder. The `Data_Summary.csv` file provides a summary of the data, including the river mile, number of sensors, and start and end years.

## Scripts:

The `scripts` folder contains the `visualizer.py` script, which is used to generate the charts, and the `main.py` script, which orchestrates the data processing and visualization.

## Output:

The generated charts are saved in the `output/charts` folder.

## Dynamic Data Handling:

The code is designed to handle data dynamically. It uses the `Data_Summary.csv` file to guide the processing of different river miles and their respective sensors. This allows the code to adapt to new data files and sensor configurations as they become available.

The code also includes checks for missing data and skips chart generation for empty datasets.

## Setup:

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

## Usage:

1. Place raw Excel files in the `data/raw/` directory.

2. Run the main script:

    ```bash
    python scripts/main.py
    ```

3. View processed data in `data/processed/` and generated charts in `output/charts/`.

## Running Tests:

To run the unit tests:

```bash
pytest
```

Edit the config.yaml file to adjust settings such as data directory paths, River Miles, sensor configurations, and chart parameters.
  
## Contributing:

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.  

## Roadmap:

See the open issues for a list of proposed features (and known issues).  

## Authors:

Abhi Mehrotra - abhimehro  

## Acknowledgments:

We welcome contributions to the Hydrograph-Versus-Seatek-Sensors-Project! Please follow these guidelines to help us review and accept your changes. 
 
## How to Contribute:

1. Fork the repository: Click the "Fork" button at the top right of this repository and clone your fork locally.
2. Create a branch: Create a new branch for your changes.
   git checkout -b my-feature-branch
   
## License:

This project is licensed under the MIT License - see the LICENSE.md file for details.  

## Contact:

Abhi Mehrotra - <abhimhrtr@pm.com>  

## Project Link:

https://github.com/abhimehro/Hydrograph-Versus-Seatek-Sensors-Project


