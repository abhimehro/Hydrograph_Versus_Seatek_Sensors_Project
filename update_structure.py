# update_structure.py
import os

def create_directory_structure():
    """Create the project directory structure."""
    directories = [
        'src/data_processing',
        'src/visualization',
        'src/utils',
        'tests',
        'config',
        'data/raw',
        'data/processed',
        'output/charts',
        'docs/technical',
        'docs/visualization'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        init_file = os.path.join(directory, '__init__.py')
        if 'src' in directory or 'tests' in directory:
            open(init_file, 'a').close()
        gitkeep = os.path.join(directory, '.gitkeep')
        if 'data' in directory or 'output' in directory:
            open(gitkeep, 'a').close()


if __name__ == '__main__':
    create_directory_structure()