"""Tests for api missing optional dependency handling."""

import sys
from types import ModuleType
from typing import Any

import pytest

# ruff: noqa: ANN401
# pyright: reportPrivateUsage=false


class TestApiMissingDependencies:
    """Test that api missing dependencies are handled gracefully with stubs."""

    def test_api_imports_are_available(self) -> None:
        """Test that api imports work (will be real in test environment)."""
        from mirascope import api

        # Should be importable without error
        assert api.Mirascope is not None
        assert api.AsyncMirascope is not None
        assert api.get_settings is not None
        assert api.settings is not None

    def test_stub_module_if_missing_with_missing_package(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test stub_module_if_missing when package is not installed."""
        import builtins

        from mirascope import _stubs
        from mirascope._stubs import stub_module_if_missing

        # Add fake extra to EXTRA_IMPORTS
        monkeypatch.setitem(
            _stubs.EXTRA_IMPORTS, "fake_api_package", ["fake_api_package"]
        )

        # Mock __import__ to raise ImportError for test package
        original_import = builtins.__import__

        def mock_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:
            if name == "fake_api_package":
                raise ImportError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        # Should return False and install stub
        result = stub_module_if_missing("test.fake.api.module", "fake_api_package")
        assert result is False
        assert "test.fake.api.module" in sys.modules

        # Clean up
        del sys.modules["test.fake.api.module"]

    def test_stub_creates_helpful_error_messages(self) -> None:
        """Test that stub error messages mention api."""
        from mirascope._stubs import _StubModule

        stub = _StubModule("test.api.module", "api")
        stub_class = stub.SomeApiClass

        with pytest.raises(
            ImportError,
            match="The 'api' packages are required to use SomeApiClass",
        ):
            stub_class()

    def test_api_classes_can_be_used_in_type_hints(self) -> None:
        """Test that api classes can be used in type hints without failing."""
        from mirascope import api

        # Should be able to use in type hints without errors
        def function_with_hint(x: api.Mirascope) -> api.Mirascope:  # type: ignore
            return x

        # Should be able to pass around the class itself
        classes = [api.Mirascope, api.AsyncMirascope]
        assert len(classes) == 2
