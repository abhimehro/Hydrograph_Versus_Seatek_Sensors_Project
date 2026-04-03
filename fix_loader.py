with open("utils/data_loader.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip_next = False
for i, line in enumerate(lines):
    if "validate_file_size" in line:
        if (
            i + 1 < len(lines)
            and "validate_file_size" in lines[i + 1]
            and lines[i] == lines[i + 1]
        ):
            # It's duplicated, only append one
            new_lines.append(line)
            skip_next = True
        elif not skip_next:
            new_lines.append(line)
        elif skip_next:
            skip_next = False  # We just skipped the duplicate
    else:
        new_lines.append(line)

with open("utils/data_loader.py", "w") as f:
    f.writelines(new_lines)
