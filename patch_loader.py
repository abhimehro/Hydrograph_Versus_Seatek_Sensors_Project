"""
Deprecated script.

This module previously performed an in-place patch of `utils/data_loader.py`.
It has been intentionally disabled to avoid keeping one-off source-mutation
utilities in the repository. If you need the old behavior, please retrieve it
from version control history instead of running this script.
"""

if __name__ == "__main__":
    raise RuntimeError(
        "patch_loader.py is deprecated and must not be used to modify source files."
    )
