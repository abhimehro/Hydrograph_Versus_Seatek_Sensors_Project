import os
import shutil
from pathlib import Path

def create_directory_structure():
    """Create and organize the project directory structure."""
    # Core directories
    directories = [
        'src/data_processing',
        'src/visualization',
        'src/utils',
        'tests/data_processing',
        'tests/visualization',
        'tests/utils',
        'config',
        'data/raw',
        'data/processed',
        'output/charts',
        'docs/technical',
        'docs/visualization'
    ]
    
    # Create directories and add __init__.py files
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        if 'src' in directory or 'tests' in directory:
            Path(f"{directory}/__init__.py").touch()
        if 'data' in directory or 'output' in directory:
            Path(f"{directory}/.gitkeep").touch()

    # Move files to correct locations
    file_moves = [
        ('scripts/other_scripts/data_loader.py', 'src/data_processing/'),
        ('scripts/other_scripts/visualizer.py', 'src/visualization/'),
    ]
    
    for src, dest in file_moves:
        if os.path.exists(src):
            shutil.move(src, dest)

    # Clean up unnecessary directories
    cleanup_dirs = [
        'scripts/other_scripts',
        'scripts',
        'objects',
        'hooks',
        'info',
        'refs'
    ]
    
    for directory in cleanup_dirs:
        if os.path.exists(directory):
            shutil.rmtree(directory)

if __name__ == '__main__':
    create_directory_structure()
    print("Project structure organized successfully!")
