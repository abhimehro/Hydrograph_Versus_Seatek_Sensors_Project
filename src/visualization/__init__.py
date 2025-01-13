"""
Visualization package for Hydrograph vs Seatek Sensors analysis.

This package provides tools for creating and managing visualizations of sensor data,
including time series plots, trend analysis, and statistical summaries.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Union, Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

# Type aliases for clarity
TimeSeriesData = pd.DataFrame
Statistics = Dict[str, float]
VisualizationResult = Tuple[Figure, Statistics]


class HydrographProcessingError(Exception):
    """Base exception for Hydrograph processing errors."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.context = context or {}

    def __str__(self):
        base_message = super().__str__()
        if self.context:
            return f"{base_message} | Context: {self.context}"
        return base_message

    def log_error(self, logger):
        """Logs the error using the provided logger."""
        logger.error(self.__str__())

    def to_dict(self) -> Dict[str, Any]:
        """Converts the exception details to a dictionary."""
        return {
            'message': str(self),
            'context': self.context
        }


@dataclass
class PlotConfig:
    """Configuration settings for plot styling."""

    dpi: int = 100
    figsize: Tuple[int, int] = (12, 8)
    font_family: str = "sans-serif"
    font_size: int = 10
    title_size: int = 16
    label_size: int = 12
    grid_alpha: float = 0.3
    scatter_alpha: float = 0.7
    scatter_size: int = 50

    @property
    def rcparams(self) -> Dict[str, Any]:
        """Get matplotlib rc parameters from config."""
        return {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial"],
            "font.size": self.font_size,
            "axes.titleweight": "bold",
            "axes.titlesize": self.title_size,
            "axes.labelsize": self.label_size,
            "figure.titlesize": self.title_size,
            "figure.dpi": self.dpi,
            "savefig.bbox": "tight",
            "figure.figsize": self.figsize,
        }


class Visualizer:
    """Class for creating sensor data visualizations."""

    def __init__(self, config: Optional[PlotConfig] = None):
        """
        Initialize the visualizer with optional custom configuration.

        Args:
            config: Optional PlotConfig object for custom styling
        """
        self.config = config or PlotConfig()
        self.setup_plot_style()

    def setup_plot_style(self) -> None:
        """Configure plot styling using seaborn and matplotlib."""
        sns.set_style("whitegrid", {
            "grid.linestyle": "--",
            "grid.alpha": self.config.grid_alpha,
            "axes.edgecolor": "0.2",
            "axes.linewidth": 1.2,
            "grid.color": "0.8",
        })
        plt.rcParams.update(self.config.rcparams)

    def create_visualization(
            self,
            data: TimeSeriesData,
            river_mile: float,
            year: int,
            sensor: str
    ) -> VisualizationResult:
        """
        Create a visualization for sensor data.

        Args:
            data: DataFrame containing time series data
            river_mile: River mile location
            year: Year of data
            sensor: Name of the sensor column

        Returns:
            Tuple containing:
                - Figure object
                - Dictionary of statistics

        Raises:
            ValueError: If required columns are missing or data is invalid
        """
        self._validate_data(data, sensor)

        try:
            fig, ax = plt.subplots()
            fig.patch.set_facecolor("white")

            # Process time data
            time_hours = self._convert_time_to_hours(data["Time (Seconds)"])

            # Create visualization elements
            scatter = self._create_scatter_plot(ax, time_hours, data[sensor])
            stats = self._calculate_statistics(data[sensor])
            self._add_trend_line(ax, time_hours, data[sensor])
            self._customize_plot(ax, scatter, river_mile, year, sensor, stats)

            plt.tight_layout()
            return fig, stats

        except Exception as e:
            plt.close(fig)  # Clean up on error
            raise VisualizationError(
                f"Error creating visualization for RM {river_mile}, "
                f"Year {year}, {sensor}: {str(e)}"
            )

    def _validate_data(self, data: TimeSeriesData, sensor: str) -> None:
        """Validate input data requirements."""
        if "Time (Seconds)" not in data.columns:
            raise ValueError("Missing required 'Time (Seconds)' column")
        if sensor not in data.columns:
            raise ValueError(f"Missing required sensor column: {sensor}")
        if len(data) < 2:
            raise ValueError("Insufficient data points for visualization")

    @staticmethod
    def _convert_time_to_hours(time_seconds: pd.Series) -> pd.Series:
        """Convert time from seconds to hours."""
        return time_seconds / 3600.0

    def _create_scatter_plot(
            self,
            ax: plt.Axes,
            time_hours: pd.Series,
            sensor_data: pd.Series
    ) -> plt.scatter:
        """Create scatter plot with sensor data."""
        return ax.scatter(
            time_hours,
            sensor_data,
            c=sensor_data,
            cmap='viridis',
            alpha=self.config.scatter_alpha,
            s=self.config.scatter_size
        )

    @staticmethod
    def _calculate_statistics(data: pd.Series) -> Statistics:
        """Calculate basic statistics for sensor data."""
        return {
            "mean": data.mean(),
            "std": data.std(),
            "min": data.min(),
            "max": data.max()
        }

    @staticmethod
    def _add_trend_line(
            ax: plt.Axes,
            time_hours: pd.Series,
            sensor_data: pd.Series
    ) -> None:
        """Add trend line to the plot."""
        coeffs = np.polyfit(time_hours, sensor_data, 1)
        trend = np.poly1d(coeffs)
        ax.plot(
            time_hours,
            trend(time_hours),
            "r--",
            alpha=0.8,
            label=f"Trend Line (slope: {coeffs[0]:.2e})"
        )

    def _customize_plot(
            self,
            ax: plt.Axes,
            scatter: plt.scatter,
            river_mile: float,
            year: int,
            sensor: str,
            stats: Statistics
    ) -> None:
        """Apply custom styling to the plot."""
        plt.colorbar(scatter, ax=ax, label=f"{sensor} Value [mm]")

        ax.set_xlabel("Time (Hours)", fontsize=self.config.label_size)
        ax.set_ylabel(f"{sensor} Reading [mm]", fontsize=self.config.label_size)

        ax.set_title(
            f"River Mile {river_mile} | {sensor} | Year {year}\n"
            f"Mean: {stats['mean']:.2f} mm | Std: {stats['std']:.2f} mm\n"
            f"Range: [{stats['min']:.2f}, {stats['max']:.2f}] mm"
        )

        ax.grid(True, linestyle="--", alpha=self.config.grid_alpha)
        ax.legend()


class VisualizationError(Exception):
    """Custom exception for visualization errors."""
    pass


# Make commonly used components available at package level
__all__ = ['Visualizer', 'PlotConfig', 'VisualizationError']