"""Utilities for stubbing modules with missing optional dependencies."""

import sys
from collections.abc import MutableSequence, Sequence
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Any

# ruff: noqa: ANN401

# Mapping of extra names to their import names
# This mapping is automatically generated from pyproject.toml
# To regenerate: uv run python scripts/generate_extra_imports.py --overwrite
# BEGIN GENERATED - DO NOT EDIT MANUALLY
EXTRA_IMPORTS: dict[str, list[str]] = {
    "anthropic": ["anthropic"],
    "api": ["pydantic_settings"],
    "google": [
        "google.genai",
        "PIL",
        "proto",
    ],
    "openai": ["openai"],
    "mcp": ["mcp"],
    "ops": [
        "opentelemetry.sdk",
        "opentelemetry",
        "opentelemetry.instrumentation",
        "opentelemetry.exporter.otlp",
        "opentelemetry.propagators.b3",
        "orjson",
        "opentelemetry.propagators.jaeger",
        "libcst",
        "packaging",
        "opentelemetry.instrumentation.openai_v2",
        "opentelemetry.instrumentation.anthropic",
        "opentelemetry.instrumentation.google_genai",
    ],
    "mlx": ["mlx_lm"],
}
# END GENERATED


def _make_import_error(package_name: str, name: str) -> ImportError:
    """Create an ImportError with a helpful installation message.

    Args:
        package_name: The package/extra name (e.g., "ops", "api")
        name: The specific item being accessed (e.g., "trace", "settings")

    Returns:
        ImportError with installation instructions
    """
    return ImportError(
        f"The '{package_name}' packages are required to use {name}. "
        f"Install them with: `uv add 'mirascope[{package_name}]'`. "
        "Or use `uv add 'mirascope[all]'` to support all optional features."
    )


class _StubMeta(type):
    """Metaclass for stub classes that fail on actual use.

    This metaclass allows stub classes to be used transparently in type hints,
    class definitions, and passed around as values, but fails with a helpful
    error when actually used (instantiated, methods called, attributes accessed).
    """

    _package_name: str
    _stub_name: str

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Raise ImportError when trying to instantiate the stub class."""
        raise _make_import_error(cls._package_name, cls._stub_name)

    def __getattr__(cls, name: str) -> Any:
        """Raise ImportError when accessing class attributes (except private/dunder)."""
        # Allow private/dunder attributes to raise AttributeError normally
        if name.startswith("_"):
            raise AttributeError(name)
        raise _make_import_error(cls._package_name, cls._stub_name)

    def __instancecheck__(cls, instance: Any) -> bool:
        """Raise ImportError when checking isinstance()."""
        raise _make_import_error(cls._package_name, cls._stub_name)

    def __subclasscheck__(cls, subclass: Any) -> bool:
        """Allow the stub to be subclassed, but raise ImportError for issubclass checks.

        This allows code like `class MyTrace(Trace): pass` to work
        at definition time. The subclass will inherit _StubMeta, so using IT
        will also fail appropriately.
        """
        if subclass is cls:
            return True
        # For issubclass() checks with other classes, fail
        raise _make_import_error(cls._package_name, cls._stub_name)


def _create_stub(package_name: str, name: str) -> type:
    """Create a universal stub that works as a class or callable.

    Args:
        package_name: The package/extra name (e.g., "ops", "api")
        name: The name of the item being stubbed (e.g., "trace", "settings")

    Returns:
        A stub class with _StubMeta metaclass
    """
    return _StubMeta(
        name,
        (),
        {
            "_package_name": package_name,
            "_stub_name": name,
            "__module__": f"mirascope.{package_name}",
        },
    )


class _StubLoader(Loader):
    """Loader that creates stub modules for missing submodules."""

    def __init__(self, fullname: str, package_name: str) -> None:
        """Initialize the stub loader.

        Args:
            fullname: The full module name being loaded
            package_name: The package/extra name for error messages
        """
        self.fullname = fullname
        self.package_name = package_name

    def create_module(self, spec: ModuleSpec) -> ModuleType:
        """Create a stub module.

        Args:
            spec: The module spec

        Returns:
            A new _StubModule instance
        """
        return _StubModule(self.fullname, self.package_name)

    def exec_module(self, module: ModuleType) -> None:
        """Execute the module (no-op for stubs).

        Args:
            module: The module to execute
        """
        pass  # Stub modules don't need execution


class _StubFinder(MetaPathFinder):
    """Meta path finder that intercepts imports for stubbed modules."""

    def __init__(self) -> None:
        """Initialize the stub finder."""
        self.stubbed_modules: set[str] = set()

    def register_stub(self, module_path: str) -> None:
        """Register a module path as stubbed.

        Args:
            module_path: The full module path that's been stubbed
        """
        self.stubbed_modules.add(module_path)

    def find_spec(
        self, fullname: str, path: Any = None, target: Any = None
    ) -> ModuleSpec | None:
        """Find a module spec for stubbed submodules.

        Args:
            fullname: The full name of the module being imported
            path: The path to search (unused)
            target: The target module (unused)

        Returns:
            A ModuleSpec if this is a submodule of a stubbed module, None otherwise
        """
        # Check if this import is for a submodule of any stubbed module
        for stub_root in self.stubbed_modules:
            if fullname.startswith(f"{stub_root}."):
                # Extract the package name from the stub root
                # e.g., "mirascope.llm.providers.openai" -> find package_name
                if fullname in sys.modules and isinstance(
                    sys.modules[fullname], _StubModule
                ):
                    # Already stubbed
                    return None

                # Get the package_name from the parent stub module
                parent_module = sys.modules.get(stub_root)
                if isinstance(parent_module, _StubModule):
                    # Use the parent's package name
                    package_name = parent_module._StubModule__package_name
                    return ModuleSpec(
                        fullname,
                        _StubLoader(fullname, package_name),
                        is_package=True,
                    )

        return None


# Global finder instance
_finder = _StubFinder()


class _StubModule(ModuleType):
    """A module that returns stubs for all attribute access.

    This allows the entire module to be stubbed, so any imports from it will
    work transparently for type checking but fail with helpful errors on actual use.

    For nested module imports like `from .openai.completions.provider import X`,
    this dynamically registers child stub modules in sys.modules when accessed.

    Each stub module instance can also act like a stub class - it can be called,
    subclassed, and used in isinstance/issubclass checks, all of which fail with
    helpful error messages.
    """

    def __init__(self, name: str, package_name: str) -> None:
        """Initialize the stub module.

        Args:
            name: The full module name (e.g., "mirascope.ops._internal.tracing")
            package_name: The package/extra name for error messages (e.g., "ops")
        """
        super().__init__(name)
        self.__package_name = package_name
        self.__stub_name = name.split(".")[-1]  # Use last part for error messages
        self.__stubs: dict[str, Any] = {}
        # Set __path__ to make this look like a package to Python's import system
        # This allows nested imports like `from .openai.completions import X` to work
        self.__path__: MutableSequence[str] = []

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Raise ImportError when trying to instantiate/call the stub.

        Raises:
            ImportError: With installation instructions
        """
        raise _make_import_error(self.__package_name, self.__stub_name)

    def __getattr__(self, name: str) -> Any:
        """Return a stub for any accessed attribute.

        For nested imports like `from .openai.completions.provider import X`, the
        _StubFinder will create intermediate stub modules automatically. This method
        handles direct attribute access for both getting submodules and getting
        classes/functions from the stub.

        Args:
            name: The attribute name being accessed

        Returns:
            Either a stub module (if already in sys.modules) or a stub class

        Raises:
            AttributeError: For private/dunder attributes
        """
        if name.startswith("_"):
            raise AttributeError(name)

        # Check if we've already created a stub for this name
        if name in self.__stubs:
            return self.__stubs[name]

        # Check if there's a submodule already created by the finder
        full_name = f"{self.__name__}.{name}"
        if full_name in sys.modules:
            submodule = sys.modules[full_name]
            self.__stubs[name] = submodule
            return submodule

        # Otherwise return a stub class for direct attribute access
        stub_class = _create_stub(self.__package_name, name)
        self.__stubs[name] = stub_class
        return stub_class

    def __instancecheck__(self, instance: Any) -> bool:
        """Raise ImportError when checking isinstance().

        Raises:
            ImportError: With installation instructions
        """
        raise _make_import_error(self.__package_name, self.__stub_name)

    def __subclasscheck__(self, subclass: Any) -> bool:
        """Allow subclassing but raise ImportError for issubclass checks.

        Args:
            subclass: The class being checked

        Returns:
            True if checking against self

        Raises:
            ImportError: For issubclass checks with other classes
        """
        if subclass is self:
            return True
        raise _make_import_error(self.__package_name, self.__stub_name)

    def __dir__(self) -> list[str]:
        """Return empty list to avoid advertising stub names.

        Returns:
            Empty list
        """
        return []


def stub_module_if_missing(
    module_path: str,
    package_name: str | Sequence[str],
) -> bool:
    """Check if all packages for one or more extras are installed; if not, stub a module.

    This must be called BEFORE importing from the module.

    Args:
        module_path: Full module path to stub (e.g., 'mirascope.ops._internal.tracing')
        package_name: The extra name (e.g., "ops") or a sequence of extra names.
            If multiple extras are provided, the module is available only when
            all of the extras have all imports available.
            An empty sequence is a no-op and returns True (vacuously satisfied).

    Returns:
        True if all packages for all extras are available (including empty sequence),
        False if stubbed.

    Raises:
        KeyError: If package_name is not found in EXTRA_IMPORTS mapping.
    """
    package_names: tuple[str, ...]
    if isinstance(package_name, str):
        package_names = (package_name,)
    else:
        package_names = tuple(package_name)

    unknown = [name for name in package_names if name not in EXTRA_IMPORTS]
    if unknown:
        unknown_names = ", ".join(unknown)
        raise KeyError(
            f"Unknown extra '{unknown_names}'. "
            f"Available extras: {', '.join(EXTRA_IMPORTS.keys())}"
        )

    def _extra_available(extra_name: str) -> bool:
        imports_to_check = EXTRA_IMPORTS[extra_name]
        for import_name in imports_to_check:
            try:
                __import__(import_name)
            except ImportError:
                return False
        return True

    # Find the first missing extra (short-circuit to avoid unnecessary imports)
    first_missing_extra: str | None = None
    for extra_name in package_names:
        if not _extra_available(extra_name):
            first_missing_extra = extra_name
            break

    # If no extras are missing, all packages are available
    if first_missing_extra is None:
        return True

    # Use the first missing extra for the error message
    sys.modules[module_path] = _StubModule(module_path, first_missing_extra)

    # Register with the finder to handle nested imports
    _finder.register_stub(module_path)

    # Ensure the finder is in sys.meta_path (only add once)
    if _finder not in sys.meta_path:
        sys.meta_path.insert(0, _finder)

    return False
