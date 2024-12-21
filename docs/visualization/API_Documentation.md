# API Documentation

## Data Processing Module

### `DataProcessor`

Core class for handling hydrograph and sensor data processing.

```python
class DataProcessor:
    def __init__(self, file_path: str):
        """
        Initialize data processor.
        
        Args:
            file_path: Path to Excel file containing sensor data
        """
        self.file_path = file_path
        self.summary_data = None
        self.river_mile_data = {}

    def load_data(self) -> None:
        """Load and validate all data from the Excel file."""
        
    def process_river_mile(self, river_mile: float) -> pd.DataFrame:
        """
        Process data for a specific river mile.
        
        Args:
            river_mile: River mile identifier
            
        Returns:
            Processed DataFrame for the specified river mile
        """
```

## Visualization Module

### `Visualizer`

Handles creation of scientific visualizations for sensor data analysis.

```python
class Visualizer:
    def create_visualization(
        self,
        data: pd.DataFrame,
        river_mile: float,
        year: int,
        sensor: str
    ) -> Tuple[Figure, Dict[str, float]]:
        """
        Create visualization for sensor data.
        
        Args:
            data: Processed sensor data
            river_mile: River mile identifier
            year: Year of data
            sensor: Sensor identifier
            
        Returns:
            Tuple of (matplotlib figure, statistics dictionary)
        """
```

## Usage Examples

### Basic Data Processing

```python
from src.data_processing import DataProcessor

# Initialize processor
processor = DataProcessor("data/sensor_readings.xlsx")

# Load and process data
processor.load_data()

# Process specific river mile
data = processor.process_river_mile(54.0)
```

### Creating Visualizations

```python
from src.visualization import Visualizer

# Initialize visualizer
viz = Visualizer()

# Create visualization
fig, stats = viz.create_visualization(
    data=processed_data,
    river_mile=54.0,
    year=2023,
    sensor="Sensor_1"
)

# Save visualization
fig.savefig("output/visualization.png", dpi=300)
```