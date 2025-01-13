"""Visualization utilities for Seatek sensor data."""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import logging
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class SeatekVisualizer:
    """Handles visualization of Seatek sensor data with hydrograph measurements."""

    def __init__(self):
        """Initialize visualizer with professional styling."""
        self._setup_style()

    def _setup_style(self) -> None:
        """Configure professional plot styling."""
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

    def create_visualization(
            self,
            data: pd.DataFrame,
            river_mile: float,
            year: int,
            sensor: str,
            output_path: Optional[Path] = None
    ) -> Optional[plt.Figure]:
        """
        Create professional visualization with Seatek and Hydrograph data.

        Args:
            data: Processed data
            river_mile: River mile number
            year: Year of data
            sensor: Sensor column name
            output_path: Optional path to save the figure

        Returns:
            Optional[Figure]: Matplotlib figure if successful
        """
        try:
            fig, axes = self._create_base_plot()
            self._add_seatek_data(axes[0], data, sensor)

            if 'Hydrograph (Lagged)' in data.columns:
                self._add_hydrograph_data(axes[0], axes[1], data)

            self._format_plot(fig, axes[0], river_mile, year, sensor)

            if output_path:
                self._save_plot(fig, output_path)

            return fig

        except Exception as e:
            logger.error(f"Visualization error: {str(e)}")
            return None

    def _create_base_plot(self) -> Tuple[plt.Figure, Tuple[plt.Axes, plt.Axes]]:
        """Create base plot with proper styling."""
        fig, ax1 = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor("white")
        ax2 = ax1.twinx()
        return fig, (ax1, ax2)

    def _add_seatek_data(
            self,
            ax: plt.Axes,
            data: pd.DataFrame,
            sensor: str
    ) -> None:
        """Add Seatek sensor data to the plot."""
        ax.scatter(
            data['Time (Minutes)'],
            data[sensor],
            color='#FF7F0E',
            alpha=0.7,
            s=45,
            label=f'Sensor {sensor.split("_")[1]} (NAVD88)'
        )

        ax.set_xlabel('Time (Minutes)', fontsize=12, labelpad=10)
        ax.set_ylabel('Seatek Sensor Reading (NAVD88)',
                      color='#FF7F0E', fontsize=12)
        ax.tick_params(axis='y', labelcolor='#FF7F0E')
        ax.grid(True, alpha=0.2, linestyle=':')

    def _add_hydrograph_data(
            self,
            ax1: plt.Axes,
            ax2: plt.Axes,
            data: pd.DataFrame
    ) -> None:
        """Add hydrograph data to the plot."""
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

    def _format_plot(
            self,
            fig: plt.Figure,
            ax: plt.Axes,
            river_mile: float,
            year: int,
            sensor: str
    ) -> None:
        """Format plot with titles, legends, and styling."""
        plt.title(
            f'River Mile {river_mile:.1f} - Year {year}\n'
            f'Seatek Sensor {sensor.split("_")[1]} Data with Hydrograph',
            pad=20,
            fontsize=14
        )

        # Enhance spines
        for spine in ax.spines.values():
            spine.set_linewidth(1.2)

        # Add legend
        lines1, labels1 = ax.get_legend_handles_labels()
        if hasattr(ax, 'right_ax'):
            lines2, labels2 = ax.right_ax.get_legend_handles_labels()
            ax.legend(
                lines1 + lines2,
                labels1 + labels2,
                loc='upper right',
                bbox_to_anchor=(0.99, 0.99),
                framealpha=0.9,
                fontsize=11
            )
        else:
            ax.legend(
                loc='upper right',
                framealpha=0.9,
                fontsize=11
            )

        plt.tight_layout()

    def _save_plot(self, fig: plt.Figure, output_path: Path) -> None:
        """Save plot to file with proper settings."""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(
                output_path,
                dpi=300,
                bbox_inches='tight',
                facecolor='white'
            )
            logger.info(f"Saved visualization to {output_path}")
        except Exception as e:
            logger.error(f"Error saving plot to {output_path}: {str(e)}")
