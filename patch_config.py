import sys

with open("utils/config.py", "r") as f:
    content = f.read()

# Add max_file_size_bytes to __init__
if "self.max_file_size_bytes" not in content:
    target = "        self.hydro_file = self.raw_data_dir / \"Hydrograph_Seatek_Data.xlsx\"\n"
    replacement = target + "\n        # SECURITY: Prevent DoS by limiting max file size loaded into memory\n        self.max_file_size_bytes = 100 * 1024 * 1024  # 100 MB\n"
    content = content.replace(target, replacement)

with open("utils/config.py", "w") as f:
    f.write(content)

print("Updated utils/config.py")
