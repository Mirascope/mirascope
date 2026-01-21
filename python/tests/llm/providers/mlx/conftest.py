"""Configuration for MLX tests.

NOTE: MLX tests are skipped on non-macOS platforms because the `mlx` package
is only available on macOS with Apple Silicon.
"""

import sys

collect_ignore_glob = []
if sys.platform != "darwin":
    collect_ignore_glob += [
        "test_*.py",
        "*/test_*.py",
    ]
