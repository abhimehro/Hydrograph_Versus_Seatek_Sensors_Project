# Technical Documentation

## Architecture Overview

The Hydrograph vs Seatek Sensors Analysis Project has been refactored to follow a modern, modular architecture with clear separation of concerns. The codebase is now organized as a proper Python package with the following structure:

```
src/
└── hydrograph_seatek_analysis/      # Main package
    ├── core/                        # Core infrastructure
    │   ├── config.py                # Configuration management
    │   └── logger.py                # Logging utilities
    ├── data/                        # Data processing
    │   ├── data_loader.py           # Data loading utilities
    │   ├── processor.py             # Data processing logic
    │   └── validator.py             # Data validation utilities
    └── visualization/               # Visualization
        └── chart_generator.py       # Chart generation
```

The new architecture implements:

- **Dependency Injection**: Components explicitly receive their dependencies
- **Single Responsibility Principle**: Each class has a clear, focused purpose
- **Type Safety**: Comprehensive type hints throughout the codebase
- **Proper Error Handling**: Structured exception handling with detailed logging

## Component Details

### Core Components

#### Configuration (`core/config.py`)

The `Config` class manages all application settings using dataclasses for strong typing and easy serialization.

```python
@dataclass
class Config:
    """Configuration settings for the Seatek data processing pipeline."""
    
    # Base directory can be overridden via environment variable
    base_dir: Path = field(default_factory=lambda: Path(
        os.environ.get("HYDROGRAPH_BASE_DIR", Path.cwd())
    ))
    # Other settings...
```

**Example usage:**

```python
# Default configuration
config = Config()

# Custom configuration
custom_config = Config(
    base_dir=Path("/custom/data/path"),
    navd88_constants=NavdConstants(offset_a=2.0, offset_b=0.4, scale_factor=15.0),
    chart_settings=ChartSettings(dpi=200, figure_size=(10, 6))
)

# Load from dictionary (e.g., from YAML)
config_dict = {
    'base_dir': '/path/to/data',
    'navd88_constants': {'offset_a': 2.0, 'scale_factor': 15.0}
}
config_from_dict = Config.from_dict(config_dict)
```

#### Logging (`core/logger.py`)

The logging system provides structured, color-coded logs with rotation capability.

```python
def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    console: bool = True
) -> logging.Logger:
    """Create a configured logger with color support (if available)."""
    # Implementation...
```

**Example usage:**

```python
# Configure application-wide logging
configure_root_logger(
    level=logging.INFO,
    log_dir=Path("logs"),
    log_filename="sensor_visualization.log"
)

# Create a module-specific logger
logger = setup_logger(
    "data_processor", 
    level=logging.DEBUG,
    log_file="logs/processor.log"
)

# Log messages with various levels
logger.debug("Processing file: example.xlsx")
logger.info("Successfully processed 50 records")
logger.warning("Missing data detected in columns")
logger.error("Failed to process file: file not found")
```

### Data Processing Components

#### Data Loader (`data/data_loader.py`)

The `DataLoader` class handles loading and initial validation of Excel data files.

```python
class DataLoader:
    """Handles loading and initial validation of data files."""

    def __init__(self, config: Config):
        """Initialize the data loader with configuration."""
        self.config = config
        
    def load_all_data(self) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """Load all required data files."""
        # Implementation...
```

**Example usage:**

```python
config = Config()
data_loader = DataLoader(config)

# Load all data at once
summary_data, hydro_data = data_loader.load_all_data()

# Get available river miles
river_miles = DataLoader.get_available_river_miles(config.processed_dir)
print(f"Available river miles: {river_miles}")
```

#### Data Processor (`data/processor.py`)

The `SeatekDataProcessor` class handles the core data processing logic, converting sensor readings to NAVD88 elevations and filtering data.

```python
@dataclass
class SeatekDataProcessor:
    """
    Handles Seatek sensor data processing and conversion to NAVD88,
    while independently filtering sensor and hydrograph streams and merging them.
    """
    data_dir: Path
    summary_data: pd.DataFrame
    config: Config
    # Other fields...
```

**Example usage:**

```python
processor = SeatekDataProcessor(
    data_dir=config.processed_dir,
    summary_data=summary_data,
    config=config
)

# Load river mile data
processor.load_data()

# Process data for a specific river mile, year, and sensor
processed_data, metrics = processor.process_data(
    river_mile=54.0,
    year=1,
    sensor="Sensor_1"
)

# Examine processing metrics
print(f"Processed {metrics.valid_rows} records")
print(f"Found {metrics.null_values} null values and {metrics.zero_values} zero values")
```

#### Data Validator (`data/validator.py`)

The `DataValidator` class provides data validation utilities to ensure data files have the correct structure and content.

```python
class DataValidator:
    """Validates data files and structure."""
    
    def __init__(self, config: Config):
        """Initialize validator with configuration."""
        self.config = config
        
    def run_validation(self) -> Dict[str, Any]:
        """Run full validation on all data files."""
        # Implementation...
```

**Example usage:**

```python
validator = DataValidator(config)

# Validate specific files
summary_validation = validator.validate_summary_file()
hydro_validation = validator.validate_hydro_file()
processed_validation = validator.validate_processed_files()

# Run full validation
validation_results = validator.run_validation()
if validation_results["overall_valid"]:
    print("All data files are valid")
else:
    print("Data validation failed")
    # Examine detailed validation results
    if not validation_results["summary"]:
        print("Summary file validation failed")
```

### Visualization Components

#### Chart Generator (`visualization/chart_generator.py`)

The `ChartGenerator` class handles creation of data visualizations with professional styling.

```python
class ChartGenerator:
    """Handles creation of data visualizations."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize chart generator with optional config."""
        self.config = config
        self.chart_settings = config.chart_settings if config else ChartSettings()
        # Additional initialization...
```

**Example usage:**

```python
chart_generator = ChartGenerator(config)

# Create a chart
fig, metrics = chart_generator.create_chart(
    data=processed_data,
    river_mile=54.0,
    year=1,
    sensor="Sensor_1"
)

# Save the chart
chart_generator.save_chart(
    fig=fig,
    output_path="output/charts/RM_54.0/Year_1_Sensor_1.png",
    dpi=300
)

# Examine chart metrics
print(f"Chart includes {metrics.sensor_count} sensor points")
print(f"Time range: {metrics.time_range_min} to {metrics.time_range_max} minutes")
```

## Main Application

The `Application` class (`app.py`) ties everything together, providing a high-level interface for the entire data processing pipeline.

```python
class Application:
    """Main application class for Seatek data processing."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize application with optional config."""
        self.config = config or Config()
        # Initialize components...
        
    def run(self) -> bool:
        """Run the full processing pipeline."""
        # Implementation...
```

**Example usage:**

```python
# Simple usage with default configuration
app = Application()
success = app.run()

# Custom configuration
custom_config = Config(
    base_dir=Path("/path/to/data"),
    navd88_constants=NavdConstants(offset_a=2.0)
)
app = Application(config=custom_config)

# Run individual steps
if app.setup() and app.load_data():
    success = app.process_data()
```

## Data Format

### Summary Data

The summary data file (`Data_Summary.xlsx`) contains river mile metadata:

| River_Mile | Num_Sensors | Start_Year | End_Year | Y_Offset | Notes |
|------------|-------------|------------|----------|----------|-------|
| 54.0       | 2           | 1995 (Y01) | 2014 (Y20) | 10.5   | Example notes |
| 53.0       | 2           | 1995 (Y01) | 2014 (Y20) | 11.2   | Example notes |

### River Mile Data

Each river mile file (`RM_*.xlsx`) contains sensor readings and hydrograph data:

| Time (Seconds) | Year | Sensor_1 | Sensor_2 | Hydrograph (Lagged) |
|----------------|------|----------|----------|---------------------|
| 0              | 1    | 5.2      | 5.4      | 150                 |
| 60             | 1    | 5.3      | 5.5      | 155                 |
| 120            | 1    | 5.4      | 5.6      | 160                 |

## NAVD88 Conversion

Sensor readings are converted to NAVD88 elevations using the following formula:

```
NAVD88_value = -(raw_data + offset_a - offset_b) * scale_factor + y_offset
```

Where:
- `raw_data`: The original sensor reading
- `offset_a`: Standard offset (default: 1.9)
- `offset_b`: Standard offset correction (default: 0.32)
- `scale_factor`: Scale factor (default: 400/30.48)
- `y_offset`: River mile-specific Y offset from summary data

## Error Handling and Logging

The application implements comprehensive error handling at multiple levels:

1. **Function-level try/except blocks**:
   ```python
   try:
       result = function_that_may_fail()
   except Exception as e:
       logger.error(f"Operation failed: {str(e)}")
       # Handle error appropriately
   ```

2. **Component-level error handling**:
   ```python
   def process_data(self, river_mile, year, sensor):
       try:
           # Processing logic
       except ValueError as e:
           logger.error(f"Invalid data: {str(e)}")
           return pd.DataFrame(), ProcessingMetrics()
       except Exception as e:
           logger.error(f"Error processing data: {str(e)}")
           return pd.DataFrame(), ProcessingMetrics()
   ```

3. **Application-level error handling**:
   ```python
   def main():
       try:
           app = Application()
           success = app.run()
           return 0 if success else 1
       except Exception as e:
           logging.error(f"Fatal error: {str(e)}")
           return 1
   ```

## Testing

The project includes a comprehensive test suite covering all major components:

- **Unit Tests**: Testing individual functions and classes
- **Integration Tests**: Testing component interactions
- **Validation Tests**: Testing data validation logic

Run tests using pytest:

```bash
# Run all tests
python -m pytest

# Run specific test modules
python -m pytest tests/test_config.py tests/test_data_processor.py

# Run with verbose output
python -m pytest -v
```

## Command-Line Tools

The package provides two main command-line tools:

### Seatek Processor

Processes and visualizes Seatek sensor data with hydrograph measurements.

```bash
# Run directly
python seatek_processor_new.py

# If installed as package
seatek-processor
```

### Data Validator

Validates the structure and content of data files.

```bash
# Run with default options
python validate_data.py

# Output results as JSON
python validate_data.py --json

# Save results to file
python validate_data.py --output validation_results.json

# Specify custom data directory
python validate_data.py --data-dir /path/to/data
```

## Performance Considerations

### Memory Management

- Data is processed per river mile, year, and sensor to minimize memory usage
- Files are closed after reading using context managers
- Matplotlib figures are explicitly closed after saving to free memory
- Pandas operations use inplace modifications where appropriate to reduce memory footprint

### Parallelization Potential

The current implementation is sequential, but the architecture supports potential parallelization:

- Processing different river miles could be parallelized
- Processing different years/sensors could be parallelized
- Chart generation could be parallelized

## Future Improvements

1. **Parallel Processing**: Implement parallel processing for multiple river miles
2. **Caching**: Add caching for frequently accessed data
3. **Advanced Analytics**: Integrate more sophisticated statistical analysis
4. **Interactive Visualizations**: Create interactive web-based visualizations
5. **Database Integration**: Store processed data in a database for more efficient querying