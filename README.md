## Hydrograph Versus Seatek Sensors Project

![GitHub issues](https://img.shields.io/github/issues/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project)

---

## Overview

This project visualizes hydrograph and Seatek sensor data from Excel files. It processes data for multiple river miles
with varying sensor data and generates charts comparing hydrograph measurements over 20 years.

## Project Setup

### Folder Structure:
Hydrograph_Versus_Seatek_Sensors_Project/ ├── data/ # All input Excel files (e.g., RM_13.1.xlsx, Data_Summary.xlsx) ├── scripts/ # Data loader and visualization scripts ├── output/ # Generated chart files ├── docs/ # Documentation (.md files) ├── tests/ # Unit tests for scripts ├── requirements.txt # Dependencies └── config.yaml # Configurations


### Data Format:
**Source File**: `Data_Summary.xlsx`  
Contains the following columns:

- **River Mile**: River location
- **Num Sensors**: Number of Seatek sensors deployed
- **Start Year**: Starting year
- **End Year**: Ending year
- **Notes**: Additional comments

### Setup Instructions:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/abhimehro/Hydrograph-Versus-Seatek-Sensors-Project.git
   cd Hydrograph-Versus-Seatek-Sensors-Project
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. [Optional] Adjust settings (e.g., paths, parameters) in `config.yaml`.

---

## Usage

1. **Input Data**:
   - Place Excel files in the `data/` directory.
2. **Run Visualization Script**:
   ```bash
   python scripts/visualizer.py
   ```
3. **View Charts**: Generated in the `output/` folder.

---

## Sample Output

Examples of generated charts:

- River Mile 54.0, Sensor 1, Year 1  
  ![Chart 1 Example](https://raw.githubusercontent.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/main/output/RM_54.0/RM_54.0_Year_1_Sensor%201.png)

- River Mile 54.0, Sensor 2, Year 1  
  ![Chart 2 Example](https://raw.githubusercontent.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/main/output/RM_54.0/RM_54.0_Year_1_Sensor%202.png)

---

## Validation & Testing

- **Data Validation**:
   - The script uses integrity checks before generating results.

- **Unit Tests**:
  Run the provided test suite:

  ```bash
  pytest tests/
  ```

---

## Contributing

We welcome contributions! Follow these steps to propose changes:

1. **Fork the repository**:

   ```bash
   git clone <your-clone-url>
   git checkout -b my-feature-branch
   ```

2. Submit a pull request and detail your changes.

See `CONTRIBUTING.md` for more details.

---

## Authors

- **Abhi Mehrotra** - [GitHub Profile](https://github.com/abhimehro)

---

## License

This project is licensed under the MIT License. See `LICENSE.md`.

---

## Contact

For questions or suggestions:

- Abhi Mehrotra: <abhimhrtr@pm.com>
- Project Link: [GitHub](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project)
