"""Configuration for MLX tests.

NOTE: MLX tests are skipped on non-macOS platforms because the `mlx` package
is only available on macOS with Apple Silicon.
"""

import sys

import pytest


@pytest.fixture(autouse=True)
def pytest_runtest_setup() -> None:
    """Skip MLX tests if not on macOS."""
    if sys.platform != "darwin":
        pytest.skip("MLX only available on macOS")
