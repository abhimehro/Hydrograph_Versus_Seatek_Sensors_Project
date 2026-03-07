═════════ ELIR ═════════
PURPOSE: Add file size validation before parsing Excel files to prevent memory exhaustion DoS attacks in the legacy `utils/data_loader.py`.
SECURITY: Missing input size validation allowed potentially infinite-sized files to be loaded into memory. I've added a check using `pathlib.Path.stat().st_size` against `max_file_size_bytes` configuration to safely exit and raise a `ValueError` for large files.
FAILS IF: A legitimate file exceeds the newly set limit of 100MB.
VERIFY: Check tests/utils/test_data_loader.py to ensure that the mocked st_size exceeds the max file size and successfully triggers the exception without processing the file.
MAINTAIN: Update `max_file_size_bytes` inside `utils/config.py` if larger files are expected in normal operation in the future.
