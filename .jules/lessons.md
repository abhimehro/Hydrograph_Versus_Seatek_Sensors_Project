## 2024-06-02 - Testing `format_sensor_name` Function

**Learning:** When adding tests, make sure you carefully read the implementation
of the target function and ensure your tests assert the actual return values
(especially for edge cases), instead of assuming what the function should do.
The initial test implementation failed because it made incorrect assumptions
about the output. **Action:** Always verify actual behavior and test against
that behavior, or explicitly refactor the target code if the behavior is deemed
incorrect.

## 2026-10-08 - CodeScene Duplication Advisory on Test Files
**Learning:** When CodeScene flags an advisory code health rule violation for Code Duplication in test files, carefully refactoring the duplicated setup logic (like mocks) into a shared helper function resolves the issue. Ensure the refactored code correctly maintains typing (`-> Any` or `-> None` for test functions) to avoid CI regressions in `mypy` or `flake8` stages.
