"""Chart generation utilities for Seatek data visualization."""

import logging
from typing import Optional

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
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
                color='#A63600',
                alpha=1.0,
                s=45,
                edgecolors='white',
                linewidth=0.5,
                label=f'Sensor {sensor.split("_")[1]} (NAVD88)'
            )

            # Configure primary axis
            ax1.set_xlabel('Time (Minutes)', fontsize=12, labelpad=10)
            ax1.set_ylabel('Seatek Sensor Reading (NAVD88)',
                          color='#A63600', fontsize=12)
            ax1.tick_params(axis='y', labelcolor='#A63600')
            ax1.grid(True, alpha=0.2, linestyle=':')

            # Add hydrograph if available
            ax2 = None
            if 'Hydrograph (Lagged)' in data.columns:
                ax2 = self._add_hydrograph(ax1, data)

            # Collect legend handles and labels
            lines, labels = ax1.get_legend_handles_labels()
            if ax2 is not None and hasattr(ax2, 'get_legend_handles_labels'):
                lines2, labels2 = ax2.get_legend_handles_labels()
                lines.extend(lines2)
                labels.extend(labels2)

            if lines:
                ax1.legend(
                    lines,
                    labels,
                    loc='upper center',
                    bbox_to_anchor=(0.5, -0.15),
                    framealpha=1.0,
                    edgecolor='#333333',
                    ncol=2,
                    fontsize=11
                )

            # Apply formatting safely based on data types
            # X-axis time formatting
            if 'Time (Minutes)' in data.columns and pd.api.types.is_numeric_dtype(data['Time (Minutes)']):
                ax1.xaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))

            # Y-axis sensor formatting
            if sensor in data.columns and pd.api.types.is_numeric_dtype(data[sensor]):
                ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.2f}"))

            # Set title and format plot
            sensor_num = sensor.split("_")[1] if "_" in sensor else sensor
            title_text = f"River Mile {river_mile:.1f} - Year {year}\nSeatek Sensor {sensor_num} Data"
            if ax2 is not None:
                title_text += " with Hydrograph"

            plt.title(title_text, pad=20, fontsize=14)

            plt.tight_layout()
            return fig

        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}")
            plt.close('all')  # Close any open figures on error
            return None

    @staticmethod
    def _add_hydrograph(ax1: plt.Axes, data: pd.DataFrame) -> Optional[plt.Axes]:
        """Add hydrograph data to the plot."""
        try:
            ax2 = ax1.twinx()
            hydro_data = data[data['Hydrograph (Lagged)'].notna()]

            if not hydro_data.empty:
                ax2.scatter(
                    hydro_data['Time (Minutes)'],
                    hydro_data['Hydrograph (Lagged)'],
                    color='#0E5A8A',
                    alpha=1.0,
                    s=70,
                    marker='s',
                    edgecolors='white',
                    linewidth=0.5,
                    label='Hydrograph (GPM)'
                )
                ax2.set_ylabel('Hydrograph (GPM)', color='#0E5A8A', fontsize=12)
                ax2.tick_params(axis='y', labelcolor='#0E5A8A')

                if pd.api.types.is_numeric_dtype(data['Hydrograph (Lagged)']):
                    hydro_values = hydro_data['Hydrograph (Lagged)']
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
