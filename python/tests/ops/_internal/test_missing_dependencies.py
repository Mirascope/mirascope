"""Tests for ops missing optional dependency handling."""

import sys
from types import ModuleType
from typing import Any

import pytest

# ruff: noqa: ANN401
# pyright: reportPrivateUsage=false


class TestOpsMissingDependencies:
    """Test that ops missing dependencies are handled gracefully with stubs."""

    def test_ops_imports_are_available(self) -> None:
        """Test that ops imports work (will be real in test environment)."""
        from mirascope import ops

        # Should be importable without error
        assert ops.trace is not None
        assert ops.span is not None
        assert ops.configure is not None
        assert ops.session is not None

    def test_stub_module_if_missing_with_missing_package(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test stub_module_if_missing when package is not installed."""
        import builtins

        from mirascope import _stubs
        from mirascope._stubs import stub_module_if_missing

        # Add fake extra to EXTRA_IMPORTS
        monkeypatch.setitem(
            _stubs.EXTRA_IMPORTS, "fake_ops_package", ["fake_ops_package"]
        )

        # Mock __import__ to raise ImportError for test package
        original_import = builtins.__import__

        def mock_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:
            if name == "fake_ops_package":
                raise ImportError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        # Should return False and install stub
        result = stub_module_if_missing("test.fake.ops.module", "fake_ops_package")
        assert result is False
        assert "test.fake.ops.module" in sys.modules

        # Clean up
        del sys.modules["test.fake.ops.module"]

    def test_stub_creates_helpful_error_messages(self) -> None:
        """Test that stub error messages mention ops."""
        from mirascope._stubs import _StubModule

        stub = _StubModule("test.ops.module", "ops")
        stub_class = stub.SomeOpsClass

        with pytest.raises(
            ImportError,
            match="The 'ops' packages are required to use SomeOpsClass",
        ):
            stub_class()

    def test_ops_classes_can_be_used_in_type_hints(self) -> None:
        """Test that ops classes can be used in type hints without failing."""
        from mirascope import ops

        # Should be able to use in type hints without errors
        def function_with_hint(x: ops.Trace) -> ops.Trace:  # type: ignore
            return x

        # Should be able to pass around the class itself
        classes = [ops.Trace, ops.Span]
        assert len(classes) == 2
