import os
from pathlib import Path

def print_directory_structure(startpath: str = '.', indent: str = '│   '):
    """Print the directory structure in a tree-like format.
    
    Args:
        startpath: Starting directory path
        indent: Indentation string for nested items
    """
    print("Project Structure:")
    
    # Files/directories to exclude
    exclude = {
        '__pycache__',
        '.git',
        '.idea',
        '.vscode',
        'venv',
        '.venv',
        'ENV',
        'dist',
        'build',
        '*.egg-info',
        '.pytest_cache',
        '.mypy_cache',
        '.coverage',
        'htmlcov'
    }
    
    # Get all paths, sorted
    paths = sorted(Path(startpath).rglob('*'))
    
    # Track printed directories to avoid duplicates
    printed_dirs = set()
    
    for path in paths:
        # Skip excluded directories and files
        if any(ex in str(path) for ex in exclude):
            continue
        
        # Get relative path
        rel_path = path.relative_to(startpath)
        parts = rel_path.parts
        
        # Print each directory level
        for i in range(len(parts)):
            dir_path = os.path.join(*parts[:i+1])
            if dir_path not in printed_dirs:
                print(f"{indent * i}├── {parts[i]}")
                printed_dirs.add(dir_path)

if __name__ == '__main__':
    print_directory_structure()
