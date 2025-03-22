# API Documentation

This document provides details on the public API for the Hydrograph vs Seatek Sensors Analysis Project.

## Core Module

### Configuration (`core/config.py`)

#### `Config` Class

Main configuration class for the application.

```python
@dataclass
class Config:
    """Configuration settings for the Seatek data processing pipeline."""
    
    # Base directory can be overridden via environment variable
    base_dir: Path = field(default_factory=lambda: Path(
        os.environ.get("HYDROGRAPH_BASE_DIR", Path.cwd())
    ))
    # Derived paths (initialized in __post_init__)
    data_dir: Path
    raw_data_dir: Path
    processed_dir: Path 
    output_dir: Path
    
    # Data file paths
    summary_file: Path
    hydro_file: Path
    
    # Configuration objects
    navd88_constants: NavdConstants = field(default_factory=NavdConstants)
    chart_settings: ChartSettings = field(default_factory=ChartSettings)
    
    def __post_init__(self) -> None:
        """Initialize derived paths and ensure directories exist."""
        
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Create a Config instance from a dictionary."""
```

#### `NavdConstants` Class

Constants for NAVD88 conversion calculations.

```python
@dataclass
class NavdConstants:
    """Constants for NAVD88 conversion."""
    offset_a: float = 1.9
    offset_b: float = 0.32
    scale_factor: float = 400 / 30.48
```

#### `ChartSettings` Class

Settings for chart generation.

```python
@dataclass
class ChartSettings:
    """Chart configuration settings."""
    dpi: int = 300
    figure_size: Tuple[int, int] = (12, 8)
    font_family: str = 'Arial'
    font_size: int = 11
```

### Logging (`core/logger.py`)

```python
def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    console: bool = True,
    file_size_limit: int = 10_000_000,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """Create a configured logger with color support (if available)."""
    
def configure_root_logger(
    level: int = logging.INFO,
    log_dir: Optional[Union[str, Path]] = None,
    log_filename: str = "app.log"
) -> None:
    """Configure the root logger for the application."""
```

## Data Module

### Data Loader (`data/data_loader.py`)

#### `DataLoader` Class

```python
class DataLoader:
    """Handles loading and initial validation of data files."""

    def __init__(self, config: Config):
        """Initialize the data loader with configuration."""
        
    def load_all_data(self) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Load all required data files.
        
        Returns:
            Tuple containing summary data and hydrograph data
        """
        
    @staticmethod
    def get_available_river_miles(processed_dir: Path) -> List[float]:
        """
        Get list of available river miles from processed data directory.
        
        Returns:
            List of river mile values
        """
```

### Data Processor (`data/processor.py`)

#### `ProcessingMetrics` Class

```python
@dataclass
class ProcessingMetrics:
    """Metrics for data processing operations."""
    original_rows: int = 0
    invalid_rows: int = 0
    zero_values: int = 0
    null_values: int = 0
    valid_rows: int = 0

    def log_metrics(self) -> None:
        """Log processing metrics."""
```

#### `RiverMileData` Class

```python
class RiverMileData:
    """Container for river mile–specific data and metadata."""

    def __init__(self, file_path: Path):
        """
        Initialize river mile data from file.
        
        Args:
            file_path: Path to the Excel file containing river mile data
        """
        
    def load_data(self) -> None:
        """Load and validate data from the Excel file."""
```

#### `SeatekDataProcessor` Class

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
    river_mile_data: Dict[float, RiverMileData] = field(default_factory=dict)
    offsets: Dict[float, float] = field(default_factory=dict)

    def convert_to_navd88(
        self,
        data: pd.DataFrame,
        sensor: str,
        river_mile: float
    ) -> pd.DataFrame:
        """
        Convert Seatek sensor readings to NAVD88 elevation.
        
        Args:
            data: DataFrame containing sensor data
            sensor: Name of the sensor column
            river_mile: River mile for the data
            
        Returns:
            DataFrame with converted sensor readings
        """
        
    def process_data(
            self,
            river_mile: float,
            year: int,
            sensor: str
    ) -> Tuple[pd.DataFrame, ProcessingMetrics]:
        """
        Process data for a given river mile, year, and sensor.
        
        Args:
            river_mile: River mile to process
            year: Year to process
            sensor: Sensor column to process
            
        Returns:
            Tuple containing processed DataFrame and processing metrics
        """
        
    def load_data(self) -> None:
        """Load data from all river mile Excel files present in the data directory."""
```

### Data Validator (`data/validator.py`)

#### `DataValidator` Class

```python
class DataValidator:
    """Validates data files and structure."""
    
    def __init__(self, config: Config):
        """Initialize validator with configuration."""
        
    def validate_summary_file(self) -> Optional[Dict[str, Any]]:
        """
        Validate summary data file.
        
        Returns:
            Dictionary with validation results or None if validation fails
        """
        
    def validate_hydro_file(self) -> Optional[Dict[str, Any]]:
        """
        Validate hydrograph data file.
        
        Returns:
            Dictionary with validation results or None if validation fails
        """
        
    def validate_processed_files(self) -> List[Dict[str, Any]]:
        """
        Validate processed river mile files.
        
        Returns:
            List of dictionaries with validation results for each file
        """
        
    def run_validation(self) -> Dict[str, Any]:
        """
        Run full validation on all data files.
        
        Returns:
            Dictionary with validation results
        """
```

## Visualization Module

### Chart Generator (`visualization/chart_generator.py`)

#### `ChartMetrics` Class

```python
@dataclass
class ChartMetrics:
    """Metrics for chart generation."""
    sensor_count: int = 0
    hydro_count: int = 0
    time_range_min: float = 0
    time_range_max: float = 0
    sensor_min: float = 0
    sensor_max: float = 0
    hydro_min: float = 0
    hydro_max: float = 0
```

#### `ChartGenerator` Class

```python
class ChartGenerator:
    """Handles creation of data visualizations."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize chart generator with optional config."""
        
    def create_chart(
            self,
            data: pd.DataFrame,
            river_mile: float,
            year: int,
            sensor: str
    ) -> Tuple[Optional[Figure], ChartMetrics]:
        """
        Create visualization for the given data.
        
        Args:
            data: DataFrame containing processed data
            river_mile: River mile for the data
            year: Year for the data
            sensor: Sensor name
            
        Returns:
            Tuple containing Figure object and ChartMetrics
        """
        
    def save_chart(
        self, 
        fig: Figure, 
        output_path: str, 
        dpi: Optional[int] = None
    ) -> bool:
        """
        Save chart to file.
        
        Args:
            fig: Figure to save
            output_path: Path to save the figure to
            dpi: Optional DPI override
            
        Returns:
            True if successful, False otherwise
        """
```

## Application Module

### Main Application (`app.py`)

#### `Application` Class

```python
class Application:
    """Main application class for Seatek data processing."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize application with optional config."""
        
    def setup(self) -> bool:
        """
        Set up application environment.
        
        Returns:
            True if successful, False otherwise
        """
        
    def load_data(self) -> bool:
        """
        Load data from files.
        
        Returns:
            True if successful, False otherwise
        """
        
    def process_data(self) -> bool:
        """
        Process data and generate visualizations.
        
        Returns:
            True if successful, False otherwise
        """
        
    def run(self) -> bool:
        """
        Run the full processing pipeline.
        
        Returns:
            True if successful, False otherwise
        """
```

## Command-Line Tools

### Seatek Processor (`seatek_processor_new.py`)

```python
def main() -> int:
    """
    Main entry point for the application.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
```

### Data Validator (`validate_data.py`)

```python
def main():
    """
    Main function for data validation.
    
    Command-line arguments:
        --json: Output validation results as JSON
        --output: Output file for validation results
        --data-dir: Base data directory (overrides default)
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
```

## Usage Examples

### Configuration Setup

```python
# Default configuration
config = Config()

# Custom configuration
custom_config = Config(
    base_dir=Path("/custom/data/path"),
    navd88_constants=NavdConstants(offset_a=2.0, offset_b=0.4, scale_factor=15.0),
    chart_settings=ChartSettings(dpi=200, figure_size=(10, 6))
)
```

### Data Loading and Processing

```python
# Initialize components
config = Config()
data_loader = DataLoader(config)

# Load data
summary_data, hydro_data = data_loader.load_all_data()

# Initialize processor
processor = SeatekDataProcessor(
    data_dir=config.processed_dir,
    summary_data=summary_data,
    config=config
)

# Load river mile data
processor.load_data()

# Process specific river mile, year, and sensor
processed_data, metrics = processor.process_data(
    river_mile=54.0,
    year=1,
    sensor="Sensor_1"
)

# Log metrics
metrics.log_metrics()
```

### Visualization Generation

```python
# Initialize chart generator
chart_generator = ChartGenerator(config)

# Create chart
fig, metrics = chart_generator.create_chart(
    data=processed_data,
    river_mile=54.0,
    year=1,
    sensor="Sensor_1"
)

# Save chart
output_path = config.output_dir / "RM_54.0" / "Year_1_Sensor_1.png"
output_path.parent.mkdir(parents=True, exist_ok=True)
chart_generator.save_chart(fig, output_path)
```

### Using the Application Class

```python
# Create application
app = Application()

# Run the full pipeline
success = app.run()

# Or run steps individually
if app.setup() and app.load_data():
    success = app.process_data()
```

### Data Validation

```python
# Initialize validator
validator = DataValidator(config)

# Run full validation
results = validator.run_validation()

# Check results
if results["overall_valid"]:
    print("All data files are valid")
else:
    print("Validation failed")
```