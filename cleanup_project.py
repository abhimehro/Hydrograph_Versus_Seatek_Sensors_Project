import os
import shutil
from pathlib import Path

def cleanup_project():
    """Clean up and organize project structure."""
    # Remove temporary files
    temp_files = [
        'update_structure.py',
        'organize_project.py',
        'show_structure.py'
    ]
    
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
    
    # Remove dist directory
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Ensure all necessary directories exist
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
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        if 'src' in directory or 'tests' in directory:
            Path(f"{directory}/__init__.py").touch()
        if 'data' in directory or 'output' in directory:
            Path(f"{directory}/.gitkeep").touch()
    
    # Clean up documentation files
    docs_cleanup = [
        ('docs/# Contributing', 'docs/CONTRIBUTING.md'),
        ('docs/# MIT License', 'docs/LICENSE.md'),
        ('docs/technical/Technical Documentation', 'docs/technical/technical_documentation.md')
    ]
    
    for old, new in docs_cleanup:
        if os.path.exists(old):
            os.rename(old, new)

if __name__ == '__main__':
    cleanup_project()
    print("Project cleanup completed successfully!")
