🔒 Sentinel: High Fix File Size Validation in data_validator.py

🎯 **What:** The vulnerability fixed
Added a file size validation check before reading `Data_Summary.xlsx`, `Hydrograph_Seatek_Data.xlsx`, and `RM_54.0.xlsx` using `pd.read_excel()` and `pd.ExcelFile()`. The fix utilizes the existing `Config` class to retrieve the `max_file_size_bytes` limit.

⚠️ **Risk:** The potential impact if left unfixed
Without limiting the size of loaded files, an extremely large file could be provided, causing memory exhaustion when parsed by pandas, leading to a Denial of Service (DoS).

🛡️ **Solution:** How the fix addresses the vulnerability
The solution instantiates the `Config` class and calls `path.stat().st_size` on each file path before processing. If the size exceeds `config.max_file_size_bytes` (100MB), a `ValueError` is raised, preventing the potentially malicious or malformed file from consuming memory.

✅ **Verification:**
Tests pass utilizing existing setup. No new failing unit tests.

═════════ ELIR ═════════
PURPOSE: Limit file sizes before reading them into memory via pandas.
SECURITY: Prevents memory exhaustion/Denial of Service (DoS) attacks.
FAILS IF: A legitimate file exceeds 100MB, although config allows overrides if necessary.
VERIFY: Confirm the `st_size` check is executed for all paths.
MAINTAIN: If adding more files to validation, ensure they are also included in the size validation loop.
