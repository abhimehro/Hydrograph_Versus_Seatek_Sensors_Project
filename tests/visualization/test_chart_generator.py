import pytest
import pandas as pd
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from src.hydrograph_seatek_analysis.visualization.chart_generator import ChartGenerator, ChartMetrics, SEATEK_COLOR, HYDRO_COLOR
from src.hydrograph_seatek_analysis.core.config import Config

@pytest.fixture
def chart_generator():
    return ChartGenerator()

@pytest.fixture
def chart_generator_with_config():
    config = Config()
    config.chart_settings.figure_size = (12, 8)
    config.chart_settings.dpi = 150
    return ChartGenerator(config)

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "Time (Minutes)": [1.0, 2.0, 3.0, 4.0],
        "Sensor_1": [10.5, 11.2, 10.8, 12.1],
        "Hydrograph (Lagged)": [100.0, 150.0, 130.0, 160.0]
    })

def test_chart_generator_init(chart_generator_with_config):
    assert chart_generator_with_config.config is not None
    assert chart_generator_with_config.chart_settings.figure_size == (12, 8)
    assert chart_generator_with_config.chart_settings.dpi == 150

def test_create_chart_success(chart_generator, sample_data):
    fig, metrics = chart_generator.create_chart(
        data=sample_data,
        river_mile=10.5,
        year=2023,
        sensor="Sensor_1"
    )

    assert isinstance(fig, Figure)
    assert isinstance(metrics, ChartMetrics)

    # Assert metrics
    assert metrics.sensor_count == 4
    assert metrics.hydro_count == 4
    assert metrics.time_range_min == 1.0
    assert metrics.time_range_max == 4.0
    assert metrics.sensor_min == 10.5
    assert metrics.sensor_max == 12.1
    assert metrics.hydro_min == 100.0
    assert metrics.hydro_max == 160.0

    # Assert chart properties
    ax1 = fig.axes[0]
    assert ax1.get_xlabel() == "Time (Minutes)"
    assert ax1.get_ylabel() == "Seatek Sensor Reading (NAVD88)"
    assert len(fig.axes) == 2 # Should have twin axis for hydrograph
    ax2 = fig.axes[1]
    assert ax2.get_ylabel() == "Hydrograph (GPM)"

def test_create_chart_no_hydrograph(chart_generator):
    data = pd.DataFrame({
        "Time (Minutes)": [1.0, 2.0, 3.0],
        "Sensor_2": [5.0, 6.0, 7.0]
    })

    fig, metrics = chart_generator.create_chart(
        data=data,
        river_mile=12.0,
        year=2024,
        sensor="Sensor_2"
    )

    assert isinstance(fig, Figure)
    assert metrics.sensor_count == 3
    assert metrics.hydro_count == 0
    assert metrics.hydro_min == 0
    assert metrics.hydro_max == 0

    assert len(fig.axes) == 1 # No twin axis

def test_create_chart_empty_data(chart_generator):
    data = pd.DataFrame(columns=["Time (Minutes)", "Sensor_1", "Hydrograph (Lagged)"])

    fig, metrics = chart_generator.create_chart(
        data=data,
        river_mile=10.0,
        year=2022,
        sensor="Sensor_1"
    )

    assert isinstance(fig, Figure)
    assert metrics.sensor_count == 0
    assert metrics.hydro_count == 0

def test_create_chart_missing_columns(chart_generator):
    data = pd.DataFrame({
        "RandomCol": [1, 2, 3]
    })

    fig, metrics = chart_generator.create_chart(
        data=data,
        river_mile=10.0,
        year=2022,
        sensor="Sensor_1"
    )

    assert isinstance(fig, Figure)
    assert metrics.sensor_count == 0
    assert metrics.time_range_max == 0

def test_create_chart_exception_handling(chart_generator, mocker):
    mocker.patch("matplotlib.pyplot.subplots", side_effect=Exception("Test Error"))

    data = pd.DataFrame({"Time (Minutes)": [1.0], "Sensor_1": [1.0]})

    fig, metrics = chart_generator.create_chart(
        data=data,
        river_mile=10.0,
        year=2022,
        sensor="Sensor_1"
    )

    assert fig is None
    assert isinstance(metrics, ChartMetrics)
