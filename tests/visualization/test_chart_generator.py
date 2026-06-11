import pytest
import pandas as pd
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from src.hydrograph_seatek_analysis.visualization.chart_generator import ChartGenerator, ChartMetrics
from src.hydrograph_seatek_analysis.core.config import Config

@pytest.fixture
def chart_generator():
    return ChartGenerator()

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "Time (Minutes)": [1.0, 2.0, 3.0, 4.0],
        "Sensor_1": [10.5, 11.2, 10.8, 12.1],
        "Hydrograph (Lagged)": [100.0, 150.0, 130.0, 160.0]
    })

def test_chart_generator_init():
    config = Config()
    config.chart_settings.figure_size = (12, 8)
    config.chart_settings.dpi = 150
    cg = ChartGenerator(config)
    assert cg.config is not None
    assert cg.chart_settings.figure_size == (12, 8)
    assert cg.chart_settings.dpi == 150

def test_create_chart_success(chart_generator, sample_data):
    fig, metrics = chart_generator.create_chart(
        data=sample_data, river_mile=10.5, year=2023, sensor="Sensor_1"
    )

    assert isinstance(fig, Figure)
    assert metrics.sensor_count == 4
    assert metrics.hydro_count == 4
    assert metrics.time_range_min == 1.0
    assert metrics.time_range_max == 4.0
    assert metrics.sensor_min == 10.5
    assert metrics.sensor_max == 12.1
    assert metrics.hydro_min == 100.0
    assert metrics.hydro_max == 160.0
    assert len(fig.axes) == 2

@pytest.mark.parametrize("scenario", [
    {
        "data": pd.DataFrame({"Time (Minutes)": [1.0, 2.0], "Sensor_2": [5.0, 6.0]}),
        "sensor": "Sensor_2",
        "sensor_count": 2,
        "hydro_count": 0,
        "axes": 1
    },
    {
        "data": pd.DataFrame(columns=["Time (Minutes)", "Sensor_1", "Hydrograph (Lagged)"]),
        "sensor": "Sensor_1",
        "sensor_count": 0,
        "hydro_count": 0,
        "axes": 1
    },
    {
        "data": pd.DataFrame({"RandomCol": [1, 2, 3]}),
        "sensor": "Sensor_1",
        "sensor_count": 0,
        "hydro_count": 0,
        "axes": 1
    }
])
def test_create_chart_edge_cases(chart_generator, scenario):
    fig, metrics = chart_generator.create_chart(
        data=scenario["data"],
        river_mile=12.0,
        year=2024,
        sensor=scenario["sensor"]
    )

    assert isinstance(fig, Figure)
    assert metrics.sensor_count == scenario["sensor_count"]
    assert metrics.hydro_count == scenario["hydro_count"]
    assert len(fig.axes) == scenario["axes"]

def test_create_chart_exception_handling(chart_generator, mocker):
    mocker.patch("matplotlib.pyplot.subplots", side_effect=Exception("Test Error"))
    fig, metrics = chart_generator.create_chart(
        data=pd.DataFrame({"Time (Minutes)": [1.0], "Sensor_1": [1.0]}),
        river_mile=10.0,
        year=2022,
        sensor="Sensor_1"
    )
    assert fig is None
    assert isinstance(metrics, ChartMetrics)
