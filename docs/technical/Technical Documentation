# Technical Documentation

## Script Architecture
The `sensor-visualization.py` script is built using a modular, object-oriented architecture consisting of three main classes:

### DataProcessor
Handles all data loading and preprocessing operations.

```python
class DataProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.summary_data = None
        self.river_mile_data = {}
```

Key responsibilities:
- Loading Excel files
- Managing multiple data sheets
- Initial data validation

### Visualizer
Manages all visualization-related operations.

```python
class Visualizer:
    def __init__(self):
        self.setup_plot_style()
```

Features:
- Consistent plot styling
- Scatter plot generation
- Trend line analysis
- Statistical calculations

### DataAnalyzer
Coordinates the overall data processing and visualization workflow.

```python
class DataAnalyzer:
    def __init__(self, data_processor: DataProcessor, visualizer: Visualizer):
        self.data_processor = data_processor
        self.visualizer = visualizer
```

Responsibilities:
- Orchestrating data processing
- Managing output directory structure
- Coordinating visualization generation

## Data Structure
The Excel file contains multiple sheets:

1. **Summary Sheet (Sheet 1)**
   ```python
   summary_data = {
       'River_Mile': float,
       'Num_Sensors': int,
       'Start_Year': str,  # Format: "1995 (Y01)"
       'End_Year': str,    # Format: "2014 (Y20)"
       'Notes': str
   }
   ```

2. **River Mile Sheets (RM_*)**
   ```python
   river_mile_data = {
       'Time (Seconds)': float,
       'Year': int,
       'Sensor_1': float,
       'Sensor_2': float,
       # Additional columns as needed
   }
   ```

## Visualization Details

### Scatter Plot Generation
```python
scatter = ax.scatter(
    time_hours,
    data[sensor],
    c=data[sensor],  # Color mapping
    cmap='viridis',
    alpha=0.7,
    s=50
)
```

Features:
- Color-coded by sensor value
- Time conversion to hours
- Alpha transparency for overlapping points

### Trend Analysis
```python
z = np.polyfit(time_hours, data[sensor], 1)
p = np.poly1d(z)
ax.plot(time_hours, p(time_hours), "r--", alpha=0.8)
```

Statistical metrics calculated:
- Mean
- Standard deviation
- Range (min/max)
- Trend line slope

## Performance Considerations

### Memory Management
- Data is processed per river mile and year
- Files are closed after reading
- Figures are cleaned up after saving

### Error Handling
Comprehensive error handling at multiple levels:
1. File loading
2. Data validation
3. Visualization creation
4. Output saving

## Output Structure
The script creates a hierarchical output structure:

```
output/
├── RM_54.0/
│   ├── Sensor_1/
│   │   ├── RM_54.0_Year_1_Sensor_1.png
│   │   └── ...
│   └── Sensor_2/
│       ├── RM_54.0_Year_1_Sensor_2.png
│       └── ...
└── ...
```

## Dependencies

Key libraries used:
- pandas (2.2.3): Data processing
- matplotlib (3.7.3): Visualization
- numpy (2.2.0): Numerical operations
- seaborn (0.13.0): Plot styling

## Best Practices Implemented

1. **Type Hints**
   ```python
   def create_visualization(
       self,
       data: pd.DataFrame,
       river_mile: float,
       year: int,
       sensor: str
   ) -> Tuple[Figure, Dict[str, float]]:
   ```

2. **Exception Handling**
   ```python
   try:
       # Operation
   except Exception as e:
       logging.error(f"Error message: {str(e)}")
       raise
   ```

3. **Logging**
   ```python
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s'
   )
   ```

## Further Development

Potential improvements:
1. Add parallel processing for multiple river miles
2. Implement caching for frequently accessed data
3. Add more advanced statistical analysis
4. Create interactive visualizations

## Testing

The script can be tested using:
```bash
pytest tests/test_sensor_visualization.py
```

Key test areas:
1. Data loading
2. Visualization generation
3. Statistical calculations
4. Error handling

## Configuration

Key parameters that can be modified:
- Figure sizes
- Color schemes
- Output directory structure
- Statistical calculations