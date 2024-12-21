import os

def print_directory_structure(startpath, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = ['.git', '__pycache__', '.idea', '.venv', 'venv']
    print("Project Structure:")
    for root, dirs, files in os.walk(startpath):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        level = root.count(os.sep)
        indent = '│   ' * level
        
        # Print directory name
        dirname = os.path.basename(root)
        if dirname != '.':
            print(f'{indent}├── {dirname}/')
        
        # Print files
        subindent = '│   ' * (level + 1)
        for f in sorted(files):
            if not f.startswith('.') and not f == 'show_structure.py':
                print(f'{subindent}├── {f}')

if __name__ == '__main__':
    print_directory_structure('.')