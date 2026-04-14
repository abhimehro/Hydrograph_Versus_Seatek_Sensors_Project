"""Chart generation utilities for Seatek data visualization."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from ..core.config import ChartSettings, Config

logger = logging.getLogger(__name__)

SEATEK_COLOR = "#A63600"
HYDRO_COLOR = "#0E5A8A"
HYDROGRAPH_COL = "Hydrograph (Lagged)"
MARKER_EDGE_COLOR = "white"
MARKER_EDGE_LINEWIDTH = 0.5


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


class ChartGenerator:
    """Handles creation of data visualizations."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize chart generator with optional config.

        Args:
            config: Optional configuration, if not provided, default chart settings will be used
        """
        self.config = config
        self.chart_settings = config.chart_settings if config else ChartSettings()
        self._setup_style()

    def _setup_style(self) -> None:
        """Configure plot styling based on config."""
        sns.set_style(
            "whitegrid",
            {
                "grid.linestyle": ":",
                "grid.alpha": 0.2,
                "axes.edgecolor": "#333333",
                "axes.linewidth": 1.2,
                "grid.color": "#CCCCCC",
            },
        )

        plt.rcParams.update(
            {
                "font.family": "sans-serif",
                "font.sans-serif": [self.chart_settings.font_family],
                "font.size": self.chart_settings.font_size,
                "figure.figsize": self.chart_settings.figure_size,
                "figure.dpi": self.chart_settings.dpi,
                "savefig.bbox": "tight",
                "savefig.pad_inches": 0.2,
            }
        )

    def create_chart(
        self, data: pd.DataFrame, river_mile: float, year: int, sensor: str
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
        metrics = ChartMetrics()

        try:
            logger.debug(
                f"Creating chart for RM {river_mile}, Year {year}, Sensor {sensor}"
            )
            logger.debug(f"Data shape: {data.shape}")

            # Calculate metrics
            metrics.sensor_count = (
                data[sensor].count() if sensor in data.columns else 0
            )
            metrics.hydro_count = (
                data[HYDROGRAPH_COL].count()
                if HYDROGRAPH_COL in data.columns
                else 0
            )

            if "Time (Minutes)" in data.columns and len(data["Time (Minutes)"]) > 0:
                metrics.time_range_min = data["Time (Minutes)"].min()
                metrics.time_range_max = data["Time (Minutes)"].max()

            if sensor in data.columns and len(data[sensor]) > 0:
                metrics.sensor_min = data[sensor].min()
                metrics.sensor_max = data[sensor].max()

            if (
                "Hydrograph (Lagged)" in data.columns
                and len(data["Hydrograph (Lagged)"]) > 0
            ):
                metrics.hydro_min = data["Hydrograph (Lagged)"].min()
                metrics.hydro_max = data["Hydrograph (Lagged)"].max()

            # Create figure
            fig, ax1 = plt.subplots(figsize=self.chart_settings.figure_size)
            fig.patch.set_facecolor("white")

            # Plot Seatek data if present
            if sensor in data.columns and metrics.sensor_count > 0:
                self._add_sensor_data(ax1, data, sensor)

            # Configure primary axis
            ax1.set_xlabel("Time (Minutes)", fontsize=12, labelpad=10)
            ax1.set_ylabel(
                "Seatek Sensor Reading (NAVD88)", color=SEATEK_COLOR, fontsize=12
            )
            ax1.tick_params(axis="y", labelcolor=SEATEK_COLOR)
            ax1.grid(True, alpha=0.2, linestyle=":")

            # Format NAVD88 axis ticks with decimal precision
            ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.2f}"))

            # Format X-axis to have comma separators for large numbers
            ax1.xaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))

            # Add hydrograph if available
            ax2 = None
            if "Hydrograph (Lagged)" in data.columns and metrics.hydro_count > 0:
                ax2 = self._add_hydrograph(ax1, data)

            # Collect legend handles and labels
            lines, labels = ax1.get_legend_handles_labels()
            if ax2 is not None:
                lines2, labels2 = ax2.get_legend_handles_labels()
                lines.extend(lines2)
                labels.extend(labels2)

            if lines:
                ax1.legend(
                    lines,
                    labels,
                    loc="upper center",
                    bbox_to_anchor=(0.5, -0.15),
                    framealpha=1.0,
                    edgecolor="#333333",
                    ncol=2,
                    fontsize=11,
                )

            # Set title and format plot
            sensor_num = sensor.split("_")[1] if "_" in sensor else sensor
            title_text = f"River Mile {river_mile:.1f} - Year {year}\nSeatek Sensor {sensor_num} Data"
            if ax2 is not None:
                title_text += " with Hydrograph"

            plt.title(title_text, pad=20, fontsize=14)

            plt.tight_layout()
            return fig, metrics

        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}")
            plt.close("all")  # Close any open figures on error
            return None, metrics

    @staticmethod
    def _add_sensor_data(ax1: plt.Axes, data: pd.DataFrame, sensor: str) -> None:
        """
        Add sensor data to the plot.

        Args:
            ax1: Primary axes object
            data: DataFrame containing sensor data
            sensor: Name of the sensor column
        """
        sensor_data = data[data[sensor].notna()]

        if len(sensor_data) > 0:
            ax1.scatter(
                sensor_data["Time (Minutes)"],
                sensor_data[sensor],
                color=SEATEK_COLOR,
                alpha=1.0,
                s=45,
                edgecolors=MARKER_EDGE_COLOR,
                linewidth=MARKER_EDGE_LINEWIDTH,
                label=f'Sensor {sensor.split("_")[1] if "_" in sensor else sensor} (NAVD88)',
            )

    @staticmethod
    def _add_hydrograph(ax1: plt.Axes, data: pd.DataFrame) -> Optional[plt.Axes]:
        """
        Add hydrograph data to the plot.

        Args:
            ax1: Primary axes object
            data: DataFrame containing hydrograph data

        Returns:
            Secondary axes object if successful, None otherwise
        """
        try:
            ax2 = ax1.twinx()
            hydro_data = data[data["Hydrograph (Lagged)"].notna()]

            if len(hydro_data) > 0:
                ax2.scatter(
                    hydro_data["Time (Minutes)"],
                    hydro_data["Hydrograph (Lagged)"],
                    color=HYDRO_COLOR,
                    alpha=1.0,
                    s=70,
                    marker="s",
                    edgecolors=MARKER_EDGE_COLOR,
                    linewidth=MARKER_EDGE_LINEWIDTH,
                    label="Hydrograph (GPM)",
                )
                ax2.set_ylabel("Hydrograph (GPM)", color=HYDRO_COLOR, fontsize=12)
                ax2.tick_params(axis="y", labelcolor=HYDRO_COLOR)

                # Choose y-axis formatter based on whether hydrograph values are effectively integers
                hydro_values = hydro_data["Hydrograph (Lagged)"]
                # Compute maximum deviation from nearest integer to detect fractional values
                max_frac_deviation = (hydro_values - hydro_values.round()).abs().max()
                if pd.notna(max_frac_deviation) and max_frac_deviation < 1e-6:
                    hydro_fmt = "{x:,.0f}"
                else:
                    hydro_fmt = "{x:,.2f}"
                ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter(hydro_fmt))

            return ax2
        except Exception as e:
            logger.error(f"Error adding hydrograph: {str(e)}")
            return None

    def save_chart(
        self,
        fig: Figure,
        output_path: str,
        dpi: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Save chart to file.

        Args:
            fig: Figure to save
            output_path: Path to save the figure to
            dpi: Optional DPI override
            metadata: Optional dictionary with image metadata (e.g. Title, Description for a11y)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create parent directories if they don't exist
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save figure
            kwargs = {"dpi": dpi or self.chart_settings.dpi, "bbox_inches": "tight"}
            if metadata:
                kwargs["metadata"] = metadata

            fig.savefig(output_path, **kwargs)
            plt.close(fig)  # Free memory
            logger.info(f"Saved chart to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving chart: {str(e)}")
            return False
