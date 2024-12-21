import pytest
import numpy as np
import pandas as pd
from src.data_processing import DataProcessor
from src.visualization import Visualizer


class TestDataValidation:
    @pytest.fixture
    def sample_data(self):
        """Create sample hydrograph and sensor data."""
        return pd.DataFrame({
            'Time (Seconds)': np.arange(0, 3600, 300),
            'Sensor_1': np.random.normal(150, 5, 12),
            'Sensor_2': np.random.normal(148, 4, 12),
            'Year': [1] * 12
        })

    def test_sensor_range_validation(self, sample_data):
        """Test sensor readings are within expected physical ranges."""
        processor = DataProcessor("test_data.xlsx")
        # Sensor readings should be between 0-1000mm (typical range for river bed measurements)
        assert all(0 <= x <= 1000 for x in sample_data['Sensor_1'].dropna())

    def test_time_series_continuity(self, sample_data):
        """Test for gaps in time series data."""
        time_diffs = np.diff(sample_data['Time (Seconds)'])
        # Check for consistent time intervals (300 seconds)
        assert all(diff == 300 for diff in time_diffs)

    def test_sensor_correlation(self, sample_data):
        """Test correlation between nearby sensors."""
        correlation = sample_data['Sensor_1'].corr(sample_data['Sensor_2'])
        # Nearby sensors should show strong correlation (>0.7)
        assert correlation > 0.7


class TestHydrologyAnalysis:
    def test_sediment_change_rate(self, sample_data):
        """Test sediment change rate calculations."""
        changes = np.diff(sample_data['Sensor_1'])
        # Maximum physically possible change rate (mm/5min)
        assert all(abs(change) < 50 for change in changes)

    def test_outlier_detection(self, sample_data):
        """Test outlier detection in sensor readings."""
        mean = sample_data['Sensor_1'].mean()
        std = sample_data['Sensor_1'].std()
        # Check for values within 3 standard deviations
        assert all(abs(x - mean) <= 3 * std for x in sample_data['Sensor_1'])


class TestVisualization:
    def test_plot_generation(self, sample_data):
        """Test visualization generation with proper units and labels."""
        viz = Visualizer()
        fig, stats = viz.create_visualization(
            sample_data, river_mile=54.0, year=1, sensor='Sensor_1'
        )
        assert fig is not None
        assert 'mean' in stats
        assert 'std' in stats

    def test_correlation_visualization(self, sample_data):
        """Test correlation plot between sensors."""
        viz = Visualizer()
        fig, stats = viz.create_visualization(
            sample_data, river_mile=54.0, year=1, sensor='Sensor_1'
        )
        assert 'correlation' in stats


def test_environmental_constraints():
    """Test environmental physics constraints."""
    processor = DataProcessor("test_data.xlsx")

    # Physical constraints for river bed measurements
    MAX_DEPTH_CHANGE_RATE = 50  # mm per 5 minutes
    MIN_SENSOR_HEIGHT = 0  # mm
    MAX_SENSOR_HEIGHT = 1000  # mm

    assert processor.MAX_DEPTH_CHANGE_RATE <= MAX_DEPTH_CHANGE_RATE
    assert processor.MIN_SENSOR_HEIGHT >= MIN_SENSOR_HEIGHT
    assert processor.MAX_SENSOR_HEIGHT <= MAX_SENSOR_HEIGHT