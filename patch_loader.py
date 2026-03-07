with open("utils/data_loader.py", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if "df = pd.read_excel(self.config.summary_file)" in line:
        new_lines.append("            if self.config.summary_file.exists() and self.config.summary_file.stat().st_size > self.config.max_file_size_bytes:\n")
        new_lines.append("                raise ValueError(f\"Summary file exceeds maximum size of {self.config.max_file_size_bytes} bytes\")\n\n")
        new_lines.append(line)
    elif "excel_file = pd.ExcelFile(self.config.hydro_file)" in line:
        new_lines.append("            if self.config.hydro_file.exists() and self.config.hydro_file.stat().st_size > self.config.max_file_size_bytes:\n")
        new_lines.append("                raise ValueError(f\"Hydrograph file exceeds maximum size of {self.config.max_file_size_bytes} bytes\")\n\n")
        new_lines.append(line)
    else:
        new_lines.append(line)

with open("utils/data_loader.py", "w") as f:
    f.writelines(new_lines)

print("Updated utils/data_loader.py")
