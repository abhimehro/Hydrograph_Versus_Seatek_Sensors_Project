import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import logging
from typing import Tuple, Dict
from matplotlib.figure import Figure

class Visualizer:
    def __init__(self):
        self.setup_plot_style()

    @staticmethod
    def setup_plot_style() -> None:
        """Set up the plot style using seaborn."""
        sns.set_style("whitegrid", {
            "grid.linestyle": "--",
            "grid.alpha": 0.3,
            "axes.edgecolor": "0.2",
            "axes.linewidth": 1.2,
            "grid.color": "0.8",
        })
        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial"],
            "font.size": 10,
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "figure.titlesize": 16,
            "figure.dpi": 100,
            "savefig.bbox": "tight",
            "figure.figsize": (12, 8),
        })

    @staticmethod
    def create_visualization(
            data: pd.DataFrame,
            river_mile: float,
            year: int,
            sensor: str
    ) -> Tuple[Figure, Dict[str, float]]:
        """Create a visualization for sensor data."""
        try:
            fig, ax = plt.subplots()
            fig.patch.set_facecolor("white")

            # Convert time column from seconds to hours
            time_hours = data["Time (Seconds)"] / 3600

            # Create scatter plot
            scatter_plot = ax.scatter(
                time_hours,
                data[sensor],
                c=data[sensor],
                cmap='viridis',
                alpha=0.7,
                s=50
            )

            # Add sensor statistics
            stats = {
                "mean": data[sensor].mean(),
                "std": data[sensor].std(),
                "min": data[sensor].min(),
                "max": data[sensor].max()
            }

            # Add colorbar
            plt.colorbar(scatter_plot, ax=ax, label=f"{sensor} Value [mm]")

            # Add trend line
            trend_coefficients = np.polyfit(time_hours, data[sensor], 1)  # Fit a linear trend line
            trend_equation = np.poly1d(trend_coefficients)
            ax.plot(
                time_hours,
                trend_equation(time_hours),
                "r--",
                alpha=0.8,
                label=f"Trend Line (slope: {trend_coefficients[0]:.2e})"
            )

            # Customize plot appearance
            ax.set_xlabel("Time (Hours)", fontsize=12)
            ax.set_ylabel(f"{sensor} Reading [mm]", fontsize=12)
            ax.set_title(
                f"River Mile {river_mile} | {sensor} | Year {year}\n"
                f"Mean: {stats['mean']:.2f} mm | Std: {stats['std']:.2f} mm\n"
                f"Range: [{stats['min']:.2f}, {stats['max']:.2f}] mm"
            )
            ax.grid(True, linestyle="--", alpha=0.3)
            ax.legend()

            # Adjust layout for better fit
            plt.tight_layout()
            return fig, stats
        except Exception as e:
            logging.error(
                f"Error creating visualization for River Mile {river_mile}, Year {year}, Sensor {sensor}: {e}"
            )
            raise