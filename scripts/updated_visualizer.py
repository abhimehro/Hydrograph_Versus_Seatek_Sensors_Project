import sys
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict , List , Tuple

from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.pyplot import close, Figure, rcParams, subplots, subplots_adjust, tight_layout
from seaborn import set_style

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DataVisualizationError(Exception):
    """Custom exception for visualization-related errors."""
    pass

def get_project_root() -> Path:
    """Get the root directory of the project."""
    project_path = Path('/Users/abhimehrotra/DataspellProjects/Hydrograph-Versus-Seatek-Sensors-Project')
    if not project_path.exists():
        raise FileNotFoundError(f"Project directory not found at: {project_path}")
    return project_path

def validate_numeric_data(data: pd.Series) -> pd.Series:
    """Validate and clean numeric data in a pandas Series."""
    return data[
        (data.notna()) & (data != 0) & (data > 0) &
        (data != float('inf')) & (data != float('-inf'))
    ]

def clean_data(data: pd.DataFrame, required_columns: List[str]) -> pd.DataFrame:
    """Clean the data by validating and removing invalid entries."""
    try:
        cleaned_data = data.copy()
        for col in required_columns:
            if col not in cleaned_data.columns:
                raise DataVisualizationError(f"Required column '{col}' not found in data")
            cleaned_data[col] = validate_numeric_data(cleaned_data[col])
        cleaned_data = cleaned_data.dropna(subset=required_columns)
        if len(cleaned_data) < 2:
            raise DataVisualizationError("Insufficient valid data points after cleaning")
        return cleaned_data
    except KeyError as e1:
        raise DataVisualizationError(f"Column not found: {str( e1 )}" )
    except Exception as e1:
        raise DataVisualizationError(f"Error during data cleaning: {str( e1 )}" )

def setup_plot_style() -> None:
    """Set up the plot style using seaborn and matplotlib."""
    sns.set_style("whitegrid", {
        'grid.linestyle': '--',
        'grid.alpha': 0.3,
        'axes.edgecolor': '0.2',
        'axes.linewidth': 1.2,
        'grid.color': '0.8'
    })
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial'],
        'font.size': 10,
        'axes.titleweight': 'bold',
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'figure.titlesize': 16,
        'figure.dpi': 100,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'figure.figsize': (15, 8)
    })

def interpret_correlation(correlation: float) -> str:
    """Interpret the correlation coefficient and return a descriptive string."""
    abs_corr = abs(correlation)
    direction = "positive" if correlation >= 0 else "negative"
    if abs_corr >= 0.9:
        strength = "Very strong"
    elif abs_corr >= 0.7:
        strength = "Strong"
    elif abs_corr >= 0.5:
        strength = "Moderate"
    elif abs_corr >= 0.3:
        strength = "Weak"
    else:
        strength = "Very weak or no"
    return f"{strength} {direction} relationship"

def format_sensor_name(sensor: str) -> str:
    """Format the sensor name by replacing underscores with spaces."""
    return ' '.join(sensor.split('_'))

def create_visualization(
        plot_data: pd.DataFrame,
        rm: float,
        year: int,
        sensor: str,
        column_mappings: Dict[str, str]
) -> Tuple[plt.Figure, float]:
    """Create a visualization of the hydrograph and sensor data."""
    try:
        fig, ax1 = plt.subplots()
        fig.patch.set_facecolor('white')
        plt.subplots_adjust(top=0.9, bottom=0.15)
        time_hours = plot_data['Time_(Hours)']
        ax1.scatter(
            time_hours,
            plot_data[column_mappings['hydrograph']],
            color='blue',
            label='Hydrograph',
            s=60,
            alpha=0.7,
            zorder=3
        )
        ax1.tick_params(axis='y', labelcolor='blue', labelsize=10)
        ax1.grid(True, linestyle='--', alpha=0.3, zorder=1)
        ax2 = ax1.twinx()
        ax2.set_ylabel('Seatek Sensor Reading [mm]', color='orange', fontsize=12, labelpad=10)
        ax2.plot(
            time_hours,
            plot_data[sensor],
            color='orange',
            label=format_sensor_name(sensor),
            linewidth=1.5,
            alpha=0.7,
            zorder=2
        )
        ax2.scatter(
            time_hours,
            plot_data[sensor],
            color='orange',
            s=40,
            alpha=0.7,
            zorder=4
        )
        ax2.tick_params(axis='y', labelcolor='orange', labelsize=10)
        n_points = len(plot_data)
        correlation = plot_data[column_mappings['hydrograph']].corr(plot_data[sensor])
        title = (
            f"River Mile {rm} | {format_sensor_name(sensor)} | Year {year}\n"
            f"Correlation Coefficient: {correlation:.2f} | n={n_points} points"
        )
        plt.title(title, pad=20)
        legend_elements = [
            mpatches.Patch(color='blue', alpha=0.7, label='Hydrograph'),
            mlines.Line2D([0], [0], color='orange', alpha=0.7,
                          label=format_sensor_name(sensor),
                          marker='o', markersize=5, linewidth=1.5)
        ]
        ax1.legend(
            handles=legend_elements,
            loc='upper right',
            bbox_to_anchor=(1.15, 1),
            fontsize=10,
            framealpha=0.9
        )
        plt.tight_layout()
        return fig, correlation
    except KeyError as e2:
        raise DataVisualizationError(f"Column not found: {str( e2 )}" )
    except Exception as e2:
        raise DataVisualizationError(f"Error creating visualization: {str( e2 )}" )

def save_visualization(
    fig: plt.Figure,
    output_path: Path,
    dpi: int = 300
) -> None:
    """Save the visualization to a file."""
    try:
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
    except Exception as e3:
        raise DataVisualizationError(f"Error saving visualization: {str( e3 )}" )

def process_rm_data(rm_data: pd.DataFrame, rm: float, sensor: str) -> int:
    """Process data for a specific river mile and sensor, generating visualizations."""
    try:
        column_mappings = {
            'time': 'Time (Seconds)',
            'hydrograph': 'Hydrograph (Lagged)',
            'year': 'Year'
        }
        required_columns = [
            column_mappings['time'],
            column_mappings['hydrograph'],
            column_mappings['year'],
            sensor
        ]
        if not all(col in rm_data.columns for col in required_columns):
            logging.warning(f"Missing required columns for RM {rm}")
            return 0
        project_root = get_project_root()
        output_dir = project_root / "output" / f"RM_{rm}"
        output_dir.mkdir(parents=True, exist_ok=True)
        charts_generated = 0
        for year in sorted(rm_data[column_mappings['year']].unique()):
            try:
                year_data = rm_data[rm_data[column_mappings['year']] == year].copy()
                year_data = clean_data(year_data, [column_mappings['hydrograph'], sensor])
                year_data['Time_(Hours)'] = year_data[column_mappings['time']] / 3600
                fig, correlation = create_visualization(
                    year_data, rm, year, sensor, column_mappings
                )
                output_path = output_dir / f"RM_{rm}_Year_{year}_{format_sensor_name(sensor)}.png"
                save_visualization(fig, output_path)
                logging.info(f"Generated chart: {output_path} (Correlation: {correlation:.2f})")
                charts_generated += 1
            except DataVisualizationError as e4:
                logging.error(f"Error processing Year {year}: {str( e4 )}" )
                continue
        return charts_generated
    except Exception as e4:
        logging.error(f"Error processing RM {rm}, {sensor}: {str( e4 )}" )
        return 0

def main() -> None:
    """Main function to orchestrate the visualization process."""
    try:
        logging.info(f"Starting visualization process at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        setup_plot_style()
        project_root = get_project_root()
        data_dir = project_root / "data"
        data_summary_path = data_dir / 'Data_Summary.xlsx'
        if not data_summary_path.exists():
            raise FileNotFoundError(f"Data summary file not found: {data_summary_path}")
        data_summary = pd.read_excel(data_summary_path)
        total_charts = 0
        for _, row in data_summary.iterrows():
            rm = row["River_Mile"]
            if pd.isna(rm):
                continue
            logging.info(f"Processing River Mile: {rm}")
            rm_file_path = data_dir / f'RM_{rm}.xlsx'
            if not rm_file_path.exists():
                logging.warning(f"File not found: {rm_file_path}")
                continue
            try:
                with pd.ExcelFile(rm_file_path) as xls:
                    rm_data = pd.read_excel(xls)
                available_sensors = [col for col in rm_data.columns if col.startswith('Sensor_')]
                if not available_sensors:
                    logging.warning(f"No sensor columns found in data for RM {rm}")
                    continue
                logging.info(f"Found sensors: {[format_sensor_name(s) for s in available_sensors]}")
                for sensor in available_sensors:
                    charts = process_rm_data(rm_data, rm, sensor)
                    total_charts += charts
            except Exception as e5:
                logging.error(f"Error processing RM {rm}: {str( e5 )}" )
                continue
        logging.info(f"Processing complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Total charts generated: {total_charts}")
    except Exception as e5:
        logging.critical(f"Critical error in main function: {str( e5 )}" )
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Visualization process interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        logging.error("For detailed error information, check the logs or contact support.")
        sys.exit(1)
