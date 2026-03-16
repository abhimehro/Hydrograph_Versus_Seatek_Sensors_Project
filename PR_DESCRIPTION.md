🧹 [code health improvement] Consolidate seatek_processor.py and seatek_processor_new.py

🎯 **What:** Replaced the legacy procedural script `seatek_processor.py` with the modernized `seatek_processor_new.py` wrapper and deleted the redundant `seatek_processor_new.py` file. Also updated all documentation references to point to `seatek_processor.py`.

💡 **Why:** Having two entry points to the application creates confusion. The legacy code in `seatek_processor.py` is obsolete because the project architecture was refactored under `src/` with an object-oriented design (`app.py`). Removing the redundant file and utilizing the original name as the main wrapper streamlines the codebase and eliminates dead code.

✅ **Verification:** Verified syntax compiles successfully via `py_compile`. Executed a regex replacement against all identified documentation locations and manually verified the diff using `git diff`. Cleaned up all pycache traces. Note that unit tests via `pytest` couldn't run due to an isolated environment without the required data science dependencies (`pandas`, `numpy`).

✨ **Result:** Reduced cognitive overhead by having a single, unambiguously named entry script for the Seatek processor, keeping legacy naming but employing modern functionality.
