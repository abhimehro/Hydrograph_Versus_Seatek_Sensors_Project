with open('tests/data_processing/__init__.py', 'r') as f:
    content = f.read()

content = content.replace(
"""        try:
            # Read the summary sheet
            self.summary_data = pd.read_excel(self.file_path, sheet_name=0)""",
"""        try:
            from utils.security import validate_file_size
            from pathlib import Path
            validate_file_size(Path(self.file_path), 100 * 1024 * 1024)
            # Read the summary sheet
            self.summary_data = pd.read_excel(self.file_path, sheet_name=0)"""
)

content = content.replace(
"""            # Process each river mile sheet
            for sheet_name in sheet_names[1:]:  # Skip the summary sheet
                if sheet_name.startswith("RM_"):
                    rm_data = pd.read_excel(excel_file, sheet_name=sheet_name)""",
"""            # Process each river mile sheet
            for sheet_name in sheet_names[1:]:  # Skip the summary sheet
                if sheet_name.startswith("RM_"):
                    validate_file_size(Path(self.file_path), 100 * 1024 * 1024)
                    rm_data = pd.read_excel(excel_file, sheet_name=sheet_name)"""
)

with open('tests/data_processing/__init__.py', 'w') as f:
    f.write(content)
