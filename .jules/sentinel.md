## 2025-03-01 - Path Traversal in Data Output Paths
**Vulnerability:** The application used unvalidated values (sensor name and year) from loaded Excel files to construct local file paths for generated charts. If a malicious or malformed Excel file contained a column name with path traversal characters (like `../../../`), the application could write output files outside the intended output directory.
**Learning:** Input from external files (like Excel column headers or cell values) must be treated as untrusted user input, especially when it influences filesystem operations.
**Prevention:** Always sanitize any dynamic segment of a file path derived from external data, using an allowlist or stripping characters outside `[a-zA-Z0-9_\-\.]`.
## 2025-03-01 - Missing Path Length Constant Leads to DoS/App Crash
**Vulnerability:** A missing class-level constant `_MAX_FILENAME_LENGTH` in the Application `_sanitize_filename` function caused a runtime exception (`AttributeError`), breaking the core protection against path-length Denial of Service (DoS) and potentially crashing the app completely.
**Learning:** Security controls added (like limiting string sizes) can themselves break the application if they reference undefined variables or constants. Security checks must always be accompanied by valid parameters to function.
**Prevention:** Ensure static/class variables utilized by security methods (e.g., maximum limits, regex boundaries) are explicitly defined inside the class or config.
## 2025-03-01 - Memory Exhaustion / DoS via Pandas read_excel
**Vulnerability:** The application was using `pd.read_excel()` to load external, untrusted Excel files directly into memory without any validation of the input file size. A malicious user could supply a very large file or a "zip bomb" (since Excel files are compressed), leading to memory exhaustion and application crashes.
**Learning:** Loading complete files into memory via data science libraries (like `pandas` or `openpyxl`) must be guarded by file size checks when processing untrusted inputs.
**Prevention:** Always verify the file size (`pathlib.Path.stat().st_size`) against a reasonable predefined limit (`max_file_size_bytes`) before attempting to parse the file into memory.
