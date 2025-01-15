"""Chart generation utilities for Seatek data visualization."""

import logging
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)

class ChartGenerator:
    """Handles creation of data visualizations."""

    def __init__(self):
        self._setup_style()

    @staticmethod
    def _setup_style() -> None:
        """Configure plot styling."""
        sns.set_style("whitegrid", {
            "grid.linestyle": ":",
            "grid.alpha": 0.2,
            "axes.edgecolor": "#333333",
            "axes.linewidth": 1.2,
            "grid.color": "#CCCCCC",
        })

        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial"],
            "font.size": 11,
            "figure.figsize": (12, 8),
            "figure.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.2
        })

    def create_chart(
            self,
            data: pd.DataFrame,
            river_mile: float,
            year: int,
            sensor: str
    ) -> Optional[Figure]:
        """Create visualization for the given data."""
        try:
            logger.debug(f"Creating chart for RM {river_mile}, Year {year}, Sensor {sensor}")
            logger.debug(f"Data shape: {data.shape}")

            fig, ax1 = plt.subplots(figsize=(12, 8))
            fig.patch.set_facecolor("white")

            # Plot Seatek data
            ax1.scatter(
                data['Time (Minutes)'],
                data[sensor],
                color='#FF7F0E',
                alpha=0.7,
                s=45,
                label=f'Sensor {sensor.split("_")[1]} (NAVD88)'
            )

            # Configure primary axis
            ax1.set_xlabel('Time (Minutes)', fontsize=12, labelpad=10)
            ax1.set_ylabel('Seatek Sensor Reading (NAVD88)',
                          color='#FF7F0E', fontsize=12)
            ax1.tick_params(axis='y', labelcolor='#FF7F0E')
            ax1.grid(True, alpha=0.2, linestyle=':')

            # Add hydrograph if available
            if 'Hydrograph (Lagged)' in data.columns:
                self._add_hydrograph(ax1, data)

            # Set title and format plot
            plt.title(
                f'River Mile {river_mile:.1f} - Year {year}\n'
                f'Seatek Sensor {sensor.split("_")[1]} Data with Hydrograph',
                pad=20,
                fontsize=14
            )

            plt.tight_layout()
            return fig

        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}")
            plt.close('all')  # Close any open figures on error
            return None

    @staticmethod
    def _add_hydrograph(ax1: plt.Axes, data: pd.DataFrame) -> None:
        """Add hydrograph data to the plot."""
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
