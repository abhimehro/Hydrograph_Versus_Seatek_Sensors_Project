# Data Format Specification

## Excel File Structure

### Summary Sheet
The first sheet contains metadata about all river mile locations.

#### Required Columns
```python
{
    'River_Mile': float,      # e.g., 54.0, 53.0
    'Num_Sensors': int,       # Number of sensors at location
    'Start_Year': str,        # Format: "1995 (Y01)"
    'End_Year': str,         # Format: "2014 (Y20)"
    'Notes': str             # Additional information
}
```

Example row:
```
River_Mile  | Num_Sensors | Start_Year   | End_Year     | Notes
54.0       | 2          | 1995 (Y01)   | 2014 (Y20)   | 1, 2
```

### River Mile Sheets
Each river mile has its own sheet named `RM_{river_mile}` (e.g., `RM_54.0`)

#### Required Columns
```python
{
    'Time (Seconds)': float,  # Time since start of measurement
    'Year': int,             # Year number (1-20)
    'Sensor_1': float,       # Readings from first sensor (mm)
    'Sensor_2': float,       # Readings from second sensor (mm)
}
```

Example data:
```
Time (Seconds) | Year | Sensor_1 | Sensor_2
0             | 1    | 150.23   | 148.45
300           | 1    | 151.34   | 149.56
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
required_columns = ['River_Mile', 'Num_Sensors', 'Start_Year', 'End_Year']
assert all(col in df.columns for col in required_columns)
```

2. **River Mile Sheet Validation**
```python
required_columns = ['Time (Seconds)', 'Year', 'Sensor_1', 'Sensor_2']
assert all(col in df.columns for col in required_columns)
```

3. **Data Type Validation**
```python
# Time must be numeric and non-negative
assert (df['Time (Seconds)'] >= 0).all()

# Year must be integer between 1 and 20
assert df['Year'].between(1, 20).all()

# Sensor readings must be numeric and positive
assert (df['Sensor_1'] > 0).all()
assert (df['Sensor_2'] > 0).all()
```

## Example Data File

```excel
// Sheet1 (Summary)
River_Mile | Num_Sensors | Start_Year | End_Year   | Notes
54.0      | 2          | 1995 (Y01) | 2014 (Y20) | 1, 2
53.0      | 2          | 1995 (Y01) | 2014 (Y20) | 3, 4

// Sheet: RM_54.0
Time (Seconds) | Year | Sensor_1 | Sensor_2
0             | 1    | 150.23   | 148.45
300           | 1    | 151.34   | 149.56
...

// Sheet: RM_53.0
Time (Seconds) | Year | Sensor_1 | Sensor_2
0             | 1    | 149.87   | 147.89
300           | 1    | 150.12   | 148.34
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