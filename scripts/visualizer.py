# scripts/visualizer.py

import matplotlib.pyplot as plt
import seaborn as sns


def create_chart(data, rm, year, output_dir):
    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=data[(data["Year"] == year) & (data["RM"] == rm)],
        x="Time (Seconds)",
        y="Hydrograph",
        label="Hydrograph (Lagged)",
    )
    for sensor in data["Sensor"].unique():
        sns.lineplot(
            data=data[
                (data["Year"] == year) & (data["RM"] == rm) & (data["Sensor"] == sensor)
            ],
            x="Time (Seconds)",
            y="Sensor_Value",
            label=f"Sensor {sensor}",
        )
    plt.title(f"Sensor Seatek Vs. Hydrograph - RM {rm} Year {year}")
    plt.xlabel("Time (in seconds)")
    plt.ylabel("Values")
    plt.legend()
    plt.savefig(output_dir / f"RM_{rm}_Year_{year}.png")
    plt.close()
