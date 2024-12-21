import os
import shutil

def create_test_directory(path: str) -> None:
    """Create a test directory if it does not exist."""
    os.makedirs(path, exist_ok=True)

def remove_test_directory(path: str) -> None:
    """Remove a test directory if it exists."""
    if os.path.exists(path):
        shutil.rmtree(path)