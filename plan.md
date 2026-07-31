1. **Write and execute a Python script to inject the `is_safe_path` check into `validate_data.py`:**
   - The script will read `validate_data.py`.
   - It will add `from src.hydrograph_seatek_analysis.utils.security import is_safe_path` after line 21.
   - It will replace lines 76-77 (handling `--output` write) with a check that uses `is_safe_path(Path.cwd(), Path(args.output))`.
   - If the path is not safe, it will log an error and exit.
2. **Use `cat` to read the modified sections of `validate_data.py` to confirm the changes were applied successfully.**
3. **Execute bash command to add a journal entry to `.jules/sentinel.md`:**
   - Command: `mkdir -p .jules && cat << 'EOF' >> .jules/sentinel.md
## 2025-03-01 - [Arbitrary File Write Prevention]
**Vulnerability:** validate_data.py allows arbitrary file write via the --output argument.
**Learning:** CLI tools that accept output paths must validate them to ensure they do not write outside the intended directory.
**Prevention:** Always use a path validation utility like `is_safe_path` to verify the output path is within a safe directory (e.g., `Path.cwd()`) before opening the file for writing.
EOF`
4. **Run the test suite using `python3 -m pytest tests/`**
5. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**
6. **Submit the fix via PR using `request_code_review` and `submit` with the appropriate format:**
   - Title: "🛡️ Sentinel: [HIGH] Fix arbitrary file write vulnerability in validate_data.py"
   - Description must contain:
     - 🚨 Severity: HIGH
     - 💡 Vulnerability: `validate_data.py` allowed arbitrary file writes via the `--output` argument.
     - 🎯 Impact: An attacker could overwrite critical files on the system by supplying a malicious path (e.g., `../../etc/passwd`).
     - 🔧 Fix: Validated the output path using `is_safe_path(Path.cwd(), Path(args.output))` before writing.
     - ✅ Verification: The script now logs an error and exits if the path is unsafe.
