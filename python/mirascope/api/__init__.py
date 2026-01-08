"""The Mirascope Cloud API client."""

from .._stubs import stub_module_if_missing

# Stub modules for missing optional dependencies BEFORE importing
# This must happen before any imports from these modules
stub_module_if_missing("mirascope.api", "api")

# Now imports work regardless of which packages are installed
# ruff: noqa: E402
from .client import AsyncMirascope, Mirascope
from .settings import get_settings, settings

__all__ = ["AsyncMirascope", "Mirascope", "get_settings", "settings"]
