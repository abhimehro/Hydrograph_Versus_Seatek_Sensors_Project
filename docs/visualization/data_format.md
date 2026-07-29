# Data Format Specification

## Excel File Structure

### Summary Sheet (`Data_Summary.xlsx`)

The summary workbook lists metadata for each river-mile location.

#### Required Columns

```python
{
    'River_Mile': float,   # e.g., 54.0, 53.0
    'Y_Offset': float,     # vertical offset applied when plotting sensors
    'Num_Sensors': int,    # number of sensors at the location
}
```

Example row:

```
River_Mile | Y_Offset | Num_Sensors
54.0       | 0.0      | 2
```

Optional informational columns (e.g. Start_Year / End_Year / Notes) may appear
in some workbooks but are **not** validated by the current pipeline
(`src/hydrograph_seatek_analysis/data/validator.py` requires only the three
columns above).

### River Mile Sheets (`Hydrograph_Seatek_Data.xlsx` / processed `RM_*.xlsx`)

Each river mile has its own sheet named `RM_{river_mile}` (e.g., `RM_54.0`).

#### Required Columns

```python
{
    'Time (Seconds)': float,       # time since start of measurement
    'Year': int,                   # year index within the campaign
    'Sensor_1': float,             # readings from first sensor (mm)
    'Sensor_2': float,             # readings from additional sensors as present
    'Hydrograph (Lagged)': float,  # lagged hydrograph stream (GPM)
}
```

Example data:

```
Time (Seconds) | Year | Sensor_1 | Sensor_2 | Hydrograph (Lagged)
0              | 1    | 150.23   | 148.45   | 1200.0
300            | 1    | 151.34   | 149.56   | 1185.5
```

## Data Validation Rules

### Time Values

- Must be non-negative
- Must be in seconds
- Should be monotonically increasing within each year

### Year Values

- Integer values from 1 to 20
- Corresponds to calendar years 1995 (Y01) to 2014 (Y20)

### Sensor Readings

- Must be positive numbers
- Measured in millimeters (mm)
- NaN or empty values are excluded during processing
- Infinite values are excluded

## Sheet Naming Convention

### Summary Sheet

- Must be the first sheet in the workbook
- Name should match standard Excel default (Sheet1)

### River Mile Sheets

```
Format: RM_{river_mile}
Example: RM_54.0, RM_53.0
```

## Data Quality Checks

The script performs the following validations:

1. **Summary Sheet Validation**

```python
required_columns = ['River_Mile', 'Y_Offset', 'Num_Sensors']
assert all(col in df.columns for col in required_columns)
```

2. **River Mile Sheet Validation**

```python
required_columns = ['Time (Seconds)', 'Year', 'Sensor_1', 'Hydrograph (Lagged)']
assert all(col in df.columns for col in required_columns)
```

3. **Data Type Validation**

```python
# Time must be numeric and non-negative
assert (df['Time (Seconds)'] >= 0).all()

# Year must be integer (campaign-specific range)
assert df['Year'].between(1, 20).all()

# Sensor readings must be numeric (NaN/inf excluded during processing)
assert pd.api.types.is_numeric_dtype(df['Sensor_1'])
```

## Example Data File

```excel
// Sheet1 (Summary)
River_Mile | Y_Offset | Num_Sensors
54.0       | 0.0      | 2
53.0       | 0.0      | 2

// Sheet: RM_54.0
Time (Seconds) | Year | Sensor_1 | Sensor_2 | Hydrograph (Lagged)
0              | 1    | 150.23   | 148.45   | 1200.0
300            | 1    | 151.34   | 149.56   | 1185.5
...

// Sheet: RM_53.0
Time (Seconds) | Year | Sensor_1 | Sensor_2 | Hydrograph (Lagged)
0              | 1    | 149.87   | 147.89   | 1190.0
300            | 1    | 150.12   | 148.34   | 1175.5
...
```

## File Naming Convention

```
Format: Hydrograph_Seatek_Data (Series {number} - {description}).xlsx
Example: Hydrograph_Seatek_Data (Series 26 - Trial Runs).xlsx
```

## Best Practices

1. **Data Organization**
   - Keep one river mile per sheet
   - Maintain consistent column names
   - Include all required fields

2. **Data Quality**
   - Validate sensor readings before input
   - Document any data gaps or anomalies
   - Include relevant notes in the summary sheet

3. **File Management**
   - Store raw data files in `data/raw/`
   - Store processed files in `data/processed/`
   - Maintain version control of data files

## Common Issues and Solutions

1. **Missing Data**

   ```python
   # Handled by excluding NaN values
   data = data.dropna(subset=['Sensor_1', 'Sensor_2'])
   ```

2. **Invalid Readings**

   ```python
   # Filtered out during validation
   data = data[data['Sensor_1'] > 0]
   ```

3. **Inconsistent Time Values**
   ```python
   # Sort by time within each year
   data = data.sort_values(['Year', 'Time (Seconds)'])
   ```
