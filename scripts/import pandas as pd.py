import logging
import os
from concurrent.futures import ProcessPoolExecutor

import matplotlib.pyplot as plt
import pandas as pd
import yaml

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_file='config.yaml'):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def process_file(file_path, rm):
    try:
        logging.info(f"Processing file: {file_path}")
        df = pd.read_excel(file_path, sheet_name=None)

        processed_data = []
        for year in range(1, 21):  # Process 20 years
            sheet_name = f"Year{year}"
            if sheet_name in df:
                year_data = df[sheet_name]
                year_data['Year'] = year
                year_data['RM'] = rm
                processed_data.append(year_data)
            else:
                logging.warning(f"Sheet {sheet_name} not found in {file_path}")

        return pd.concat(processed_data, ignore_index=True)
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {str(e)}")
        return None

def create_chart(data, rm, year, sensor, chart_config):
    fig, ax1 = plt.subplots(figsize=chart_config['figsize'])

    ax2 = ax1.twinx()

    year_data = data[(data['RM'] == rm) & (data['Year'] == year)]

    ax1.plot(year_data['Time (Seconds)'], year_data[f'Hydrograph (Lagged) for Y{year:02d}'],
             color=chart_config['hydrograph_color'], label='Hydrograph (Lagged)')
    ax2.plot(year_data['Time (Seconds)'], year_data[f'Sensor {sensor} for Y{year:02d}'],
             color=chart_config['sensor_color'], label=f'Sensor {sensor}')

    ax1.set_xlabel('Time (in seconds)')
    ax1.set_ylabel('Hydrograph Flow Rate (GPM)', color=chart_config['hydrograph_color'])
    ax2.set_ylabel('Sediment Bed Levels (NAVD88)', color=chart_config['sensor_color'])

    plt.title(f'RM {rm} - Sensor {sensor} vs. Hydrograph - Year {year}')
    fig.legend(loc='upper right', bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)

    plt.tight_layout()
    output_file = f'charts/RM_{rm}_Sensor_{sensor}_Year_{year}.png'
    plt.savefig(output_file, dpi=chart_config['dpi'])
    plt.close()
    logging.info(f"Chart saved: {output_file}")

def process_rm(rm, file_path, config):
    data = process_file(file_path, rm)
    if data is not None:
        for year in range(1, 21):
            for sensor in config['rm_sensors'][str(rm)]:
                create_chart(data, rm, year, sensor, config['chart'])

def main():
    config = load_config()
    os.makedirs('charts', exist_ok=True)

    with ProcessPoolExecutor() as executor:
        futures = []
        for rm, file_name in config['rm_files'].items():
            file_path = os.path.join(config['data_dir'], file_name)
            futures.append(executor.submit(process_rm, float(rm), file_path, config))

        for future in futures:
            future.result()

if __name__ == "__main__":
    main()