import matplotlib.pyplot as plt
import pandas as pd
import pytest
import seaborn as sns
from pandas.testing import assert_frame_equal

# Remove or modify the import statement for set_color_codes if it is not needed
# from seaborn.rcmod import set_color_codes


@pytest.fixture
def sample_data():
    return pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [5, 4, 3, 2, 1]})


@pytest.fixture
def tmp_path(tmpdir):
    return tmpdir


@pytest.mark.usefixtures("sample_data", "tmp_path")
def test_data_saving(sample_data, tmp_path):
    csv_file = tmp_path / "data.csv"
    sample_data.to_csv(csv_file, index=False)

    # Load the data using the script
    loaded_data = pd.read_csv(csv_file)

    # Save the loaded data to an Excel file
    excel_file = tmp_path / "output.xlsx"
    loaded_data.to_excel(excel_file, index=False)

    # Load the data back from the Excel file
    saved_data = pd.read_excel(excel_file)

    # Check if the saved data matches the loaded data
    assert_frame_equal(loaded_data, saved_data)


@pytest.mark.usefixtures("sample_data", "tmp_path", "monkeypatch")
def test_plot_generation(sample_data, tmp_path, monkeypatch):
    csv_file = tmp_path / "data.csv"
    sample_data.to_csv(csv_file, index=False)

    # Load the data using the script
    loaded_data = pd.read_csv(csv_file)

    # Mock plt.show to avoid displaying the plot during tests
    monkeypatch.setattr(plt, "show", lambda: None)

    # Generate the plot
    sns.scatterplot(data=loaded_data, x="x", y="y")
    plt.show()

    # Check if the plot was generated (this is a basic check)
    # Save the plot to a temporary file
    plot_file = tmp_path / "plot.png"
    plt.savefig(plot_file)

    # Check if the plot file was created
    if not plot_file.exists():
        raise AssertionError("Plot file was not created")

    # Close the plot
    plt.close()
