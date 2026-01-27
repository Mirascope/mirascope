"""Tests for missing optional dependency handling."""

import builtins
import sys
from types import ModuleType
from typing import Any

import pytest

from mirascope import _stubs
from mirascope._stubs import (
    _finder,
    _make_import_error,
    _StubModule,
    stub_module_if_missing,
)

# pyright: reportPrivateUsage=false


class TestMissingDependencies:
    """Test that missing dependencies are handled gracefully with stubs."""

    def test_stub_module_creation(self) -> None:
        """Test that _StubModule works as expected."""
        stub = _StubModule("test.module", "test_package")

        # Should return a stub class for any attribute
        stub_class = stub.SomeClass
        assert stub_class is not None

        # Accessing the same attribute should return the same stub
        assert stub.SomeClass is stub_class

        # Should fail on instantiation
        with pytest.raises(
            ImportError,
            match="The 'test_package' packages are required to use SomeClass",
        ):
            stub_class()

    def test_stub_class_attribute_access(self) -> None:
        """Test that stub classes fail on attribute access."""
        stub = _StubModule("test.module", "test_package")
        stub_class = stub.SomeClass

        # Should fail on attribute access (non-private)
        with pytest.raises(
            ImportError,
            match="The 'test_package' packages are required to use SomeClass",
        ):
            _ = stub_class.some_method

    def test_stub_class_isinstance(self) -> None:
        """Test that isinstance checks fail with helpful error."""
        stub = _StubModule("test.module", "test_package")
        stub_class = stub.SomeClass

        with pytest.raises(
            ImportError,
            match="The 'test_package' packages are required to use SomeClass",
        ):
            isinstance(object(), stub_class)

    def test_stub_class_issubclass_with_other(self) -> None:
        """Test that issubclass checks fail with helpful error."""
        stub = _StubModule("test.module", "test_package")
        stub_class = stub.SomeClass

        with pytest.raises(
            ImportError,
            match="The 'test_package' packages are required to use SomeClass",
        ):
            issubclass(object, stub_class)

    def test_stub_class_issubclass_with_self(self) -> None:
        """Test that issubclass with self returns True."""
        stub = _StubModule("test.module", "test_package")
        stub_class = stub.SomeClass

        # issubclass with itself should return True
        assert issubclass(stub_class, stub_class) is True

    def test_stub_class_can_be_subclassed_in_definition(self) -> None:
        """Test that stub classes can be subclassed (but using the subclass fails)."""
        stub = _StubModule("test.module", "test_package")
        stub_class = stub.SomeClass

        # Should be able to define a subclass
        class MyClass(stub_class):
            pass

        # But using the subclass should fail (with parent's name in error)
        with pytest.raises(
            ImportError,
            match="The 'test_package' packages are required to use SomeClass",
        ):
            MyClass()

    def test_stub_private_attribute_raises_attribute_error(self) -> None:
        """Test that private attributes raise AttributeError, not ImportError."""
        stub = _StubModule("test.module", "test_package")

        with pytest.raises(AttributeError):
            _ = stub._private

        stub_class = stub.SomeClass
        with pytest.raises(AttributeError):
            _ = stub_class._private

    def test_stub_module_dir_returns_empty_list(self) -> None:
        """Test that __dir__ returns empty list for stub modules."""
        stub = _StubModule("test.module", "test_package")

        # __dir__ should return empty list
        assert dir(stub) == []

    def test_stub_module_call_raises_import_error(self) -> None:
        """Test that calling a stub module raises ImportError."""
        stub = _StubModule("test.module", "test_package")

        # Calling the module itself should fail
        with pytest.raises(
            ImportError,
            match="The 'test_package' packages are required to use module",
        ):
            stub()

    def test_stub_module_isinstance_raises_import_error(self) -> None:
        """Test that isinstance checks on stub modules raise ImportError."""
        stub = _StubModule("test.module", "test_package")

        # isinstance check with the module itself should fail
        with pytest.raises(
            ImportError,
            match="The 'test_package' packages are required to use module",
        ):
            isinstance(object(), stub)  # pyright: ignore[reportArgumentType]

    def test_stub_module_issubclass_with_other_raises_import_error(self) -> None:
        """Test that issubclass checks on stub modules raise ImportError."""
        stub = _StubModule("test.module", "test_package")

        # issubclass check with another class should fail
        with pytest.raises(
            ImportError,
            match="The 'test_package' packages are required to use module",
        ):
            issubclass(object, stub)  # pyright: ignore[reportArgumentType]

    def test_stub_module_issubclass_with_self_returns_true(self) -> None:
        """Test that issubclass with itself returns True for stub modules."""
        stub = _StubModule("test.module", "test_package")

        # issubclass with itself should return True
        assert issubclass(stub, stub) is True  # pyright: ignore[reportArgumentType]

    def test_stub_module_if_missing_with_missing_package(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test stub_module_if_missing when package is not installed."""
        # Add fake extra to EXTRA_IMPORTS
        monkeypatch.setitem(_stubs.EXTRA_IMPORTS, "fake_package", ["fake_package"])

        # Mock __import__ to raise ImportError for test package
        original_import = builtins.__import__

        def mock_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:  # noqa: ANN401
            if name == "fake_package":
                raise ImportError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        # Should return False and install stub
        result = stub_module_if_missing("test.fake.module", "fake_package")
        assert result is False
        assert "test.fake.module" in sys.modules

        # Clean up
        del sys.modules["test.fake.module"]

    def test_stub_module_if_missing_with_installed_package(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test stub_module_if_missing when package is installed."""
        # Add pytest to EXTRA_IMPORTS (it's installed in dev environment)
        monkeypatch.setitem(_stubs.EXTRA_IMPORTS, "pytest", ["pytest"])

        # Use a package we know is installed (pytest)
        result = stub_module_if_missing("test.real.module", "pytest")
        assert result is True
        # Should not install a stub
        assert "test.real.module" not in sys.modules

    def test_stub_module_if_missing_with_unknown_package(self) -> None:
        """Test stub_module_if_missing raises KeyError for unknown package."""
        # Should raise KeyError for unknown package name
        with pytest.raises(
            KeyError, match="Unknown extra 'unknown_package_xyz'"
        ) as exc_info:
            stub_module_if_missing("test.module", "unknown_package_xyz")

        # Check that the error message lists available extras
        assert "anthropic" in str(exc_info.value)
        assert "openai" in str(exc_info.value)

    def test_stub_module_if_missing_with_multiple_extras_all_available(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test stub_module_if_missing with multiple extras all available."""
        # Add fake extras that use packages we know are installed
        monkeypatch.setitem(_stubs.EXTRA_IMPORTS, "extra1", ["pytest"])
        monkeypatch.setitem(_stubs.EXTRA_IMPORTS, "extra2", ["sys"])

        # Should return True when ALL extras are available
        result = stub_module_if_missing("test.multi.all", ["extra1", "extra2"])
        assert result is True
        # Should not install a stub
        assert "test.multi.all" not in sys.modules

    def test_stub_module_if_missing_with_multiple_extras_one_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test stub_module_if_missing returns False if any extra is missing."""
        # Add fake extras: one available, one missing
        monkeypatch.setitem(_stubs.EXTRA_IMPORTS, "available_extra", ["pytest"])
        monkeypatch.setitem(_stubs.EXTRA_IMPORTS, "missing_extra", ["nonexistent_pkg"])

        # Mock __import__ to raise ImportError for the missing package
        original_import = builtins.__import__

        def mock_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:  # noqa: ANN401
            if name == "nonexistent_pkg":
                raise ImportError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        # Should return False because not ALL extras are available
        result = stub_module_if_missing(
            "test.multi.partial", ["available_extra", "missing_extra"]
        )
        assert result is False
        assert "test.multi.partial" in sys.modules

        # Verify the stub references the MISSING extra, not the first one
        stub_module = sys.modules["test.multi.partial"]
        assert isinstance(stub_module, _StubModule)
        # The error message should reference "missing_extra", not "available_extra"
        with pytest.raises(ImportError, match="missing_extra"):
            stub_module.SomeClass()

        # Clean up
        del sys.modules["test.multi.partial"]

    def test_stub_module_if_missing_with_empty_sequence(self) -> None:
        """Test stub_module_if_missing returns True for empty sequence."""
        # Empty sequence means no extras to check, so all are satisfied (vacuously true)
        result = stub_module_if_missing("test.module", [])
        assert result is True
        # Should not install a stub
        assert "test.module" not in sys.modules

    def test_error_message_format(self) -> None:
        """Test that error messages are helpful and properly formatted."""
        error = _make_import_error("anthropic", "AnthropicProvider")
        assert "anthropic" in str(error)
        assert "AnthropicProvider" in str(error)
        assert "uv add 'mirascope[anthropic]'" in str(error)
        assert "uv add 'mirascope[all]'" in str(error)

    def test_nested_import_via_finder(self) -> None:
        """Test that the finder creates stub modules for nested imports."""
        # Manually create a stub module and register it
        stub = _StubModule("test_finder_stub", "test_package")
        sys.modules["test_finder_stub"] = stub
        _finder.register_stub("test_finder_stub")

        # Ensure finder is in meta_path
        if _finder not in sys.meta_path:
            sys.meta_path.insert(0, _finder)

        try:
            # Now import a nested module - this should be created by the finder
            import test_finder_stub.nested.deep  # pyright: ignore[reportMissingImports]

            # Verify it was created
            assert "test_finder_stub.nested" in sys.modules
            assert "test_finder_stub.nested.deep" in sys.modules

            # Both should be stub modules
            assert isinstance(sys.modules["test_finder_stub.nested"], _StubModule)
            assert isinstance(sys.modules["test_finder_stub.nested.deep"], _StubModule)

            # Accessing attributes should return stub classes
            something = test_finder_stub.nested.deep.SomeClass
            assert something is not None

            # Using the stub class should fail
            with pytest.raises(
                ImportError, match="The 'test_package' packages are required"
            ):
                something()

            # Test accessing a nested module that exists in sys.modules
            # This tests the __getattr__ path (lines 244-246) where submodule is found
            # Create a fresh stub to ensure clean state
            fresh_stub = _StubModule("test_fresh", "test_pkg")
            sys.modules["test_fresh"] = fresh_stub
            # Manually create a child module in sys.modules
            child = _StubModule("test_fresh.child", "test_pkg")
            sys.modules["test_fresh.child"] = child
            # Now access it via getattr - should hit lines 244-246
            accessed_child = fresh_stub.child
            assert accessed_child is child

            # Test that importing an already-stubbed module returns None from finder
            # (the "already stubbed" path in find_spec)
            # Call find_spec directly to test the "already stubbed" path
            spec = _finder.find_spec("test_finder_stub.nested")
            assert (
                spec is None
            )  # Should return None because it's already in sys.modules

            # Test that finder returns None when parent_module is not a _StubModule
            # This covers line 188 in _stubs.py where isinstance check fails
            sys.modules["test_non_stub_parent"] = object()  # pyright: ignore[reportArgumentType]
            _finder.register_stub("test_non_stub_parent")
            spec = _finder.find_spec("test_non_stub_parent.child")
            assert spec is None

            # Test that finder returns None for non-stubbed modules
            # This exercises the final return None in find_spec
            spec = _finder.find_spec("totally.unrelated.module")
            assert spec is None

        finally:
            # Clean up
            for key in list(sys.modules.keys()):
                if key.startswith(
                    ("test_finder_stub", "test_fresh", "test_non_stub_parent")
                ):
                    del sys.modules[key]


class TestProviderStubs:
    """Test that actual provider stubs work correctly."""

    @pytest.fixture(autouse=True)
    def reload_providers(self) -> None:
        """Reload provider modules to ensure clean state."""
        # Note: We can't actually test missing dependencies in normal test runs
        # because the dependencies are installed. These tests verify the structure
        # is correct, but manual testing or CI without deps would verify actual behavior.
        pass

    def test_anthropic_provider_is_importable(self) -> None:
        """Test that AnthropicProvider can be imported (will be real or stub)."""
        from mirascope.llm.providers import AnthropicProvider

        # Should be importable without error
        assert AnthropicProvider is not None

    def test_google_provider_is_importable(self) -> None:
        """Test that GoogleProvider can be imported (will be real or stub)."""
        from mirascope.llm.providers import GoogleProvider

        # Should be importable without error
        assert GoogleProvider is not None

    def test_openai_provider_is_importable(self) -> None:
        """Test that OpenAIProvider can be imported (will be real or stub)."""
        from mirascope.llm.providers import OpenAIProvider

        # Should be importable without error
        assert OpenAIProvider is not None

    def test_mlx_provider_is_importable(self) -> None:
        """Test that MLXProvider can be imported (will be real or stub)."""
        from mirascope.llm.providers import MLXProvider

        # Should be importable without error
        assert MLXProvider is not None

    def test_together_provider_is_importable(self) -> None:
        """Test that TogetherProvider can be imported (will be real or stub)."""
        from mirascope.llm.providers import TogetherProvider

        # Should be importable without error
        assert TogetherProvider is not None

    def test_ollama_provider_is_importable(self) -> None:
        """Test that OllamaProvider can be imported (will be real or stub)."""
        from mirascope.llm.providers import OllamaProvider

        # Should be importable without error
        assert OllamaProvider is not None

    def test_openai_completions_provider_is_importable(self) -> None:
        """Test that BaseOpenAICompletionsProvider can be imported."""
        from mirascope.llm.providers import BaseOpenAICompletionsProvider

        # Should be importable without error
        assert BaseOpenAICompletionsProvider is not None

    def test_model_ids_are_importable(self) -> None:
        """Test that model ID types are importable."""
        from mirascope.llm.providers import (
            AnthropicModelId,
            GoogleModelId,
            MLXModelId,
            OpenAIModelId,
        )

        # All should be importable
        assert AnthropicModelId is not None
        assert GoogleModelId is not None
        assert OpenAIModelId is not None
        assert MLXModelId is not None

    def test_providers_can_be_passed_around(self) -> None:
        """Test that provider classes can be passed around without instantiation."""
        from mirascope.llm.providers import (
            AnthropicProvider,
            GoogleProvider,
            OpenAIProvider,
        )

        # Should be able to put in lists, dicts, etc.
        providers = [AnthropicProvider, GoogleProvider, OpenAIProvider]
        assert len(providers) == 3

        provider_map = {
            "anthropic": AnthropicProvider,
            "google": GoogleProvider,
            "openai": OpenAIProvider,
        }
        assert len(provider_map) == 3

    def test_providers_can_be_used_in_subclass_definitions(self) -> None:
        """Test that provider classes can be subclassed in definitions."""
        from mirascope.llm.providers import AnthropicProvider

        # Should be able to define a subclass without error
        class MyCustomProvider(AnthropicProvider):
            """Custom provider extending Anthropic."""

            pass

        # The class definition itself should work
        assert MyCustomProvider is not None
