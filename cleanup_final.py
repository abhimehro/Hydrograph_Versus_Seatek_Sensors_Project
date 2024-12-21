import os
from pathlib import Path

def cleanup_project():
    """Final cleanup of project structure."""
    
    # 1. Remove .DS_Store files
    for ds_store in Path('.').rglob('.DS_Store'):
        ds_store.unlink()
    
    # 2. Clean up documentation
    docs_renames = [
        ('docs/# Contributing to Hydrograph_Versus_Seatek_Sensors_Project.md', 'docs/CONTRIBUTING.md'),
        ('docs/# MIT License.md', 'docs/LICENSE.md'),
        ('docs/technical/description', 'docs/technical/project_description.md'),
        ('docs/technical/packed-refs', 'docs/technical/references.md')
    ]
    
    for old, new in docs_renames:
        if os.path.exists(old):
            os.makedirs(os.path.dirname(new), exist_ok=True)
            os.rename(old, new)
    
    # 3. Organize test files
    test_moves = [
        ('tests/test_utils.py', 'tests/utils/test_utils.py'),
        ('tests/test_visualization.py', 'tests/visualization/test_visualization.py'),
        ('tests/# test_data_processor.py', 'tests/data_processing/test_data_processor.py')
    ]
    
    for old, new in test_moves:
        if os.path.exists(old):
            os.makedirs(os.path.dirname(new), exist_ok=True)
            if os.path.exists(old):
                os.rename(old, new)
    
    # 4. Create .gitkeep files
    keep_dirs = [
        'data/raw',
        'data/processed',
        'output/charts'
    ]
    
    for directory in keep_dirs:
        os.makedirs(directory, exist_ok=True)
        Path(f"{directory}/.gitkeep").touch()

    # 5. Create necessary directories
    directories = [
        'src/data_processing',
        'src/visualization',
        'src/utils',
        'tests/data_processing',
        'tests/visualization',
        'tests/utils',
        'config',
        'docs/technical',
        'docs/visualization'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        if 'src' in directory or 'tests' in directory:
            Path(f"{directory}/__init__.py").touch()

    # 6. Update .gitignore
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
.Python
build/
develop-eggs/
dist/
*.egg-info/
*.egg

# Virtual Environment
.env
.venv/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo
.run/
.codiumai/

# Project specific
output/**/*.png
!output/.gitkeep

# Data files
data/**/*.xlsx
data/**/*.txt
!data/raw/.gitkeep
!data/processed/.gitkeep

# Temporary files
.DS_Store
*.log
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/

# Keep specific directories and their contents
!src/
!src/**
!tests/
!tests/**
!config/
!config/**
!docs/
!docs/**

# Keep specific files
!pyproject.toml
!.pre-commit-config.yaml
!README.md
!docs/**/*.md
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content.strip())

    print("Cleanup completed successfully!")
    print("\nProject structure organized:")
    print("- Removed .DS_Store files")
    print("- Organized documentation")
    print("- Structured test files")
    print("- Created necessary directories")
    print("- Updated .gitignore")

if __name__ == '__main__':
    cleanup_project()
