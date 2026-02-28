## 2025-03-01 - Path Traversal in Data Output Paths
**Vulnerability:** The application used unvalidated values (sensor name and year) from loaded Excel files to construct local file paths for generated charts. If a malicious or malformed Excel file contained a column name with path traversal characters (like `../../../`), the application could write output files outside the intended output directory.
**Learning:** Input from external files (like Excel column headers or cell values) must be treated as untrusted user input, especially when it influences filesystem operations.
**Prevention:** Always sanitize any dynamic segment of a file path derived from external data, using an allowlist or stripping characters outside `[a-zA-Z0-9_\-\.]`.
