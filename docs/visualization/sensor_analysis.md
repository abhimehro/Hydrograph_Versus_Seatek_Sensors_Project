# Sensor Analysis Documentation

## Overview
The sensor analysis module provides comprehensive time series analysis and visualization for Seatek sensor data. This guide covers the technical details, configuration options, and best practices.

## Data Structure
Each sensor's data follows this schema:
```python
{
    'Time (Seconds)': float,  # Measurement timestamp
    'Year': int,             # Year (1-20, corresponding to 1995-2014)
    'Sensor_1': float,       # First sensor readings (cm)
    'Sensor_2': float        # Second sensor readings (cm)
}
```

## Directory Structure
```
output/
├── RM_54.0/
│   └── sensor_charts/          # Sensor-specific analysis
│       ├── Sensor 1/           # First sensor visualizations
│       │   ├── RM_54.0_Year_1_Sensor_1.png
│       │   └── ...            # Years 2-20
│       └── Sensor 2/          # Second sensor visualizations
└── ... (other river miles)
```

## Visualization Features

### Time Series Analysis
- Temporal distribution of readings
- Automatic time conversion (seconds to hours)
- Trend line analysis with slope calculation
- Color-coded data points by value

### Statistical Metrics
- Mean sensor readings
- Standard deviation calculation
- Range analysis (min/max values)
- Point density visualization

### Professional Formatting
- High-resolution output (300 DPI)
- Publication-ready styling
- Clear statistical annotations
- Customizable color schemes

## Configuration

### Basic Configuration
```python
# In src/sensor-visualization_v2.py
VISUALIZATION_CONFIG = {
    'figure': {
        'dpi': 300,
        'figsize': (12, 8)
    },
    'style': {
        'grid.alpha': 0.25,
        'font.size': 11
    }
}
```

### Advanced Options
```python
# Custom styling configuration
STYLE_CONFIG = {
    'grid': {
        'linestyle': ':',
        'alpha': 0.25,
        'color': '#CCCCCC'
    },
    'scatter': {
        'marker': 'o',
        'alpha': 0.8,
        'edgecolor': 'white',
        'linewidth': 0.5
    }
}
```

## Performance Optimization

### Memory Management
```python
# Enable memory-efficient processing
PROCESSING_CONFIG = {
    'chunk_size': 1000,          # Process in chunks
    'parallel': True,            # Enable parallel processing
    'max_workers': 4,            # Number of parallel workers
    'cache_enabled': True        # Enable result caching
}
```

### Efficiency Features
- Skip processing for insufficient data
- Avoid regenerating existing visualizations
- Parallel processing support
- Memory-efficient data handling

## Error Handling
The module implements comprehensive error handling:
```python
try:
    # Process data for specific year and sensor
    year_data = data[data["Year"] == year].copy()
    
    # Validate data sufficiency
    if len(year_data) < 2:
        logging.warning(f"Insufficient data: RM {river_mile}, Year {year}")
        return False
        
    # Check for existing visualization
    if os.path.exists(output_path):
        logging.info(f"Visualization exists: {output_path}")
        return True
        
except Exception as e:
    logging.error(f"Processing error: {str(e)}")
    return False
```

## Best Practices

### Data Validation
- Verify data types and ranges
- Check for missing values
- Validate time sequences
- Ensure sufficient data points

### Output Management
- Use consistent naming conventions
- Maintain directory structure
- Implement version control
- Regular backup procedures

### Performance Monitoring
- Track processing times
- Monitor memory usage
- Log error frequencies
- Maintain audit trails

## Troubleshooting

### Common Issues
1. **Insufficient Data**
   - Check input file completeness
   - Verify year ranges
   - Validate sensor readings

2. **Memory Issues**
   - Adjust chunk size
   - Enable parallel processing
   - Implement data streaming

3. **Quality Issues**
   - Verify data cleaning
   - Check statistical outliers
   - Validate time sequences

## Advanced Usage
```python
# Key improvements that made it work
plot_data = data.copy()  # Create a copy to avoid modifying original
plot_data['time_minutes'] = plot_data['Time (Seconds)'] / 60  # Convert to minutes
plot_data[f'{sensor}_cm'] = plot_data[sensor] / 10  # Convert mm to cm

# Use converted data throughout
scatter = ax.scatter(
    plot_data['time_minutes'],
    plot_data[f'{sensor}_cm'],  # Use converted values
    c=plot_data[f'{sensor}_cm'],  # Color mapping also uses converted values
    )
```

### Custom Analysis
```python
# Example: Custom trend analysis
def analyze_trend(data, sensor):
    z = np.polyfit(data['Time (Hours)'], data[sensor], 1)
    slope = z[0]
    return {
        'slope': slope,
        'direction': 'increasing' if slope > 0 else 'decreasing',
        'magnitude': abs(slope)
    }
```

### Extended Statistics
```python
# Example: Advanced statistical analysis
def compute_statistics(data, sensor):
    return {
        'mean': data[sensor].mean(),
        'std': data[sensor].std(),
        'range': (data[sensor].min(), data[sensor].max()),
        'quartiles': data[sensor].quantile([0.25, 0.5, 0.75]),
        'skewness': data[sensor].skew()
    }
```
