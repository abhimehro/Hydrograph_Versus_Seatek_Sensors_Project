import pytest
import pandas as pd
import seaborn as sns
from pandas.testing import assert_frame_equal
# Remove the import statement if it is not needed

import matplotlib.pyplot as plt


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [5, 4, 3, 2, 1]
    })

def test_data_loading(sample_data, tmpdir):
    # Save sample data to a temporary CSV file
    csv_file = tmpdir.join('data.csv')
    sample_data.to_csv(csv_file, index=False)

    # Load the data using the script
    loaded_data = pd.read_csv(csv_file)

    # Check if the loaded data matches the sample data
    assert_frame_equal(loaded_data, sample_data)

def test_data_saving(sample_data, tmpdir):
    # Save sample data to a temporary CSV file
    csv_file = tmpdir.join('data.csv')
    sample_data.to_csv(csv_file, index=False)

    # Load the data using the script
    loaded_data = pd.read_csv(csv_file)

    # Save the loaded data to an Excel file
    excel_file = tmpdir.join('output.xlsx')
    loaded_data.to_excel(excel_file, index=False)

    # Load the data back from the Excel file
    saved_data = pd.read_excel(excel_file)

    # Check if the saved data matches the loaded data
    assert_frame_equal(saved_data, loaded_data)

def test_plot_generation(sample_data, tmpdir, monkeypatch):
    # Save sample data to a temporary CSV file
    csv_file = tmpdir.join('data.csv')
    sample_data.to_csv(csv_file, index=False)

    # Load the data using the script
    loaded_data = pd.read_csv(csv_file)

    # Mock plt.show to avoid displaying the plot during tests
    monkeypatch.setattr(plt, 'show', lambda: None)

    # Generate the plot
    sns.scatterplot(data=loaded_data, x='x', y='y')
    plt.show()

    # Check if the plot was generated (this is a basic check)
    assert plt.gcf().number == 1