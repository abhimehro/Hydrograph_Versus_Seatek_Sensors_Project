"""Chart generation utilities for Seatek data visualization."""

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from ..core.config import Config, ChartSettings

logger = logging.getLogger(__name__)


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
        sns.set_style("whitegrid", {
            "grid.linestyle": ":",
            "grid.alpha": 0.2,
            "axes.edgecolor": "#333333",
            "axes.linewidth": 1.2,
            "grid.color": "#CCCCCC",
        })

        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.sans-serif": [self.chart_settings.font_family],
            "font.size": self.chart_settings.font_size,
            "figure.figsize": self.chart_settings.figure_size,
            "figure.dpi": self.chart_settings.dpi,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.2
        })

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
        metrics = ChartMetrics()
        
        try:
            logger.debug(f"Creating chart for RM {river_mile}, Year {year}, Sensor {sensor}")
            logger.debug(f"Data shape: {data.shape}")

            # Calculate metrics
            metrics.sensor_count = data[sensor].notna().sum() if sensor in data.columns else 0
            metrics.hydro_count = data['Hydrograph (Lagged)'].notna().sum() if 'Hydrograph (Lagged)' in data.columns else 0
            
            if 'Time (Minutes)' in data.columns and not data['Time (Minutes)'].empty:
                metrics.time_range_min = data['Time (Minutes)'].min()
                metrics.time_range_max = data['Time (Minutes)'].max()
            
            if sensor in data.columns and not data[sensor].empty:
                metrics.sensor_min = data[sensor].min()
                metrics.sensor_max = data[sensor].max()
                
            if 'Hydrograph (Lagged)' in data.columns and not data['Hydrograph (Lagged)'].empty:
                metrics.hydro_min = data['Hydrograph (Lagged)'].min()
                metrics.hydro_max = data['Hydrograph (Lagged)'].max()

            # Create figure
            fig, ax1 = plt.subplots(figsize=self.chart_settings.figure_size)
            fig.patch.set_facecolor("white")

            # Plot Seatek data if present
            if sensor in data.columns and metrics.sensor_count > 0:
                self._add_sensor_data(ax1, data, sensor)

            # Configure primary axis
            ax1.set_xlabel('Time (Minutes)', fontsize=12, labelpad=10)
            ax1.set_ylabel('Seatek Sensor Reading (NAVD88)',
                          color='#CC4C02', fontsize=12)
            ax1.tick_params(axis='y', labelcolor='#CC4C02')
            ax1.grid(True, alpha=0.2, linestyle=':')

            # Add hydrograph if available
            if 'Hydrograph (Lagged)' in data.columns and metrics.hydro_count > 0:
                self._add_hydrograph(ax1, data)

            # Set title and format plot
            sensor_num = sensor.split("_")[1] if "_" in sensor else sensor
            plt.title(
                f'River Mile {river_mile:.1f} - Year {year}\n'
                f'Seatek Sensor {sensor_num} Data with Hydrograph',
                pad=20,
                fontsize=14
            )

            plt.tight_layout()
            return fig, metrics

        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}")
            plt.close('all')  # Close any open figures on error
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
        
        if not sensor_data.empty:
            ax1.scatter(
                sensor_data['Time (Minutes)'],
                sensor_data[sensor],
                color='#CC4C02',
                alpha=0.7,
                s=45,
                label=f'Sensor {sensor.split("_")[1] if "_" in sensor else sensor} (NAVD88)'
            )

    @staticmethod
    def _add_hydrograph(ax1: plt.Axes, data: pd.DataFrame) -> None:
        """
        Add hydrograph data to the plot.
        
        Args:
            ax1: Primary axes object
            data: DataFrame containing hydrograph data
        """
        try:
            ax2 = ax1.twinx()
            hydro_data = data[data['Hydrograph (Lagged)'].notna()]

            if not hydro_data.empty:
                ax2.scatter(
                    hydro_data['Time (Minutes)'],
                    hydro_data['Hydrograph (Lagged)'],
                    color='#1F77B4',
                    alpha=0.7,
                    s=70,
                    marker='s',
                    label='Hydrograph (GPM)'
                )
                ax2.set_ylabel('Hydrograph (GPM)', color='#1F77B4', fontsize=12)
                ax2.tick_params(axis='y', labelcolor='#1F77B4')

                # Add legend
                lines1, labels1 = ax1.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax1.legend(
                    lines1 + lines2,
                    labels1 + labels2,
                    loc='upper right',
                    bbox_to_anchor=(0.99, 0.99),
                    framealpha=0.9,
                    fontsize=11
                )
        except Exception as e:
            logger.error(f"Error adding hydrograph: {str(e)}")
            
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
        try:
            # Create parent directories if they don't exist
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save figure
            fig.savefig(
                output_path, 
                dpi=dpi or self.chart_settings.dpi, 
                bbox_inches='tight'
            )
            plt.close(fig)  # Free memory
            logger.info(f"Saved chart to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving chart: {str(e)}")
            return False