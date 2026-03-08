# ELIR Handoff: File Size Validation for `pd.read_excel`

📋 **PURPOSE**: Adds explicit file size validation using `pathlib.Path.stat().st_size` right before invoking `pd.read_excel()` on sheets in `utils/data_loader.py`.
🛡️ **SECURITY**: Mitigates potential Denial-of-Service (DoS) attacks and out-of-memory crashes by preventing the parsing of maliciously large or inflated files.
⚠️ **FAILS IF**: The underlying `max_file_size_bytes` limit is configured to be too small for legitimate production data.
✅ **VERIFY**: Check that `pd.read_excel()` operations correctly throw a `ValueError` with "exceeds maximum size" when processing large dummy files.
🔧 **MAINTAIN**: If `max_file_size_bytes` proves restrictive during normal operation, its value can be bumped within `utils/config.py`.
