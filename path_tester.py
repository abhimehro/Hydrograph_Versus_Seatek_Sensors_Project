from pathlib import Path
import os


def test_paths():
    """Test and print various paths to help with debugging."""
    print("\nPath Test Results:")
    print("-" * 50)

    # Current working directory
    print(f"Current working directory: {Path.cwd()}")

    # Script location
    print(f"Script location: {Path(__file__).resolve()}")

    # Walk up to find project root
    current = Path.cwd()
    print("\nWalking up directory tree:")
    while current.name:
        print(f"Checking: {current}")
        if (current / '.git').exists():
            print(f"Found .git in: {current}")
        if current.name == 'Hydrograph_Versus_Seatek_Sensors_Project':
            print(f"Found project directory: {current}")
        current = current.parent

    # Check expected data paths
    project_root = Path.cwd()
    print("\nChecking expected data paths:")
    paths_to_check = [
        project_root / "data/raw/Data_Summary.xlsx",
        project_root / "data/raw/Hydrograph_Seatek_Data.xlsx",
        project_root / "data/processed/RM_54.0.xlsx"
    ]

    for path in paths_to_check:
        exists = path.exists()
        print(f"\nPath: {path}")
        print(f"Exists: {exists}")
        if exists:
            print(f"Is file: {path.is_file()}")
            print(f"Size: {path.stat().st_size:,} bytes")

    # List contents of data directory
    print("\nContents of data directory:")
    data_dir = project_root / "data"
    if data_dir.exists():
        for item in data_dir.rglob("*"):
            if item.is_file():
                print(f"File: {item.relative_to(project_root)}")


if __name__ == "__main__":
    test_paths()