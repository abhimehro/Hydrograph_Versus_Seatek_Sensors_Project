## 2024-03-07 - Missing File Size Validation Before pandas.read_excel
**Vulnerability:** Memory exhaustion (DoS) vulnerability in data loaders lacking pre-read file size validation.
**Learning:** `pd.read_excel()` and `pd.ExcelFile()` read the entire file into memory before validation can occur, which makes the application susceptible to out-of-memory errors and DoS when parsing excessively large malicious files.
**Prevention:** Always verify the file size (`pathlib.Path.stat().st_size`) against a reasonable predefined limit (`max_file_size_bytes`) before attempting to parse the file into memory.
