"""Auto-discovery of API structure from Griffe modules.

This module provides functions to automatically discover documentable API objects
from a loaded Griffe module, generating directive strings that can be processed
by the existing documentation pipeline.
"""

import re
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from typing import NewType

from griffe import Alias, Attribute, Class, Function, Module, Object

from .type_urls import BUILTIN_TYPE_URLS

# Type aliases for better type safety
ObjectPath = NewType("ObjectPath", str)
"""Canonical path to a Python object (e.g., 'mirascope_v2_llm.calls.decorator.call')"""


class Slug(str):
    """A filesystem-safe slug matching [a-z0-9][a-z0-9-_]* pattern.

    Must start with an alphanumeric character (no leading hyphens or underscores).
    """

    _pattern = re.compile(r"^[a-z0-9][a-z0-9-_]*$")

    def __new__(cls, value: str) -> "Slug":
        if not cls._pattern.match(value):
            raise ValueError(
                f"Invalid slug '{value}': must start with [a-z0-9] and contain only [a-z0-9-_]"
            )
        return super().__new__(cls, value)

    @classmethod
    def from_name(cls, name: str) -> "Slug":
        """Create a slug from a name by converting to lowercase and replacing invalid chars."""
        slug = name.lower().replace(".", "-").replace("_", "-")
        # Remove any remaining invalid characters
        slug = re.sub(r"[^a-z0-9-_]", "", slug)
        return cls(slug)


class DirectiveType(Enum):
    CLASS = "Class"
    FUNCTION = "Function"
    MODULE = "Module"
    ALIAS = "Alias"
    ATTRIBUTE = "Attribute"


@dataclass
class RawDirective:
    object_path: ObjectPath
    object_type: DirectiveType

    def __str__(self) -> str:
        return f"::: {self.object_path}  # {self.object_type.value}"

    def symbol_name(self) -> str:
        """Extract the symbol name from the object path.

        Returns:
            The last component of the object path (e.g., "call" from "mirascope_v2_llm.calls.decorator.call")

        """
        return self.object_path.split(".")[-1]


@dataclass
class RawDirectivesPage:
    """Represents an API directive with its output path and original name.

    Attributes:
        directives: List of Directive objects for this documentation file
        directory: Directory path for nested structures (e.g., "calls" or "" for root)
        slug: The clean slug identifier (e.g., "agent" or "base-tool")
        name: The original name with proper casing (e.g., "Agent" or "agent")

    """

    directives: list[RawDirective]
    directory: str
    slug: Slug
    name: str

    @property
    def file_path(self) -> str:
        """Get the full file path with .mdx extension."""
        if self.directory:
            return f"{self.directory}/{self.slug}.mdx"
        return f"{self.slug}.mdx"


@dataclass
class ApiObject:
    """Canonical representation of an API object with all computed properties."""

    object_path: ObjectPath
    object_type: DirectiveType
    canonical_slug: Slug
    canonical_docs_path: str
    symbol_name: str


@dataclass
class Directive:
    """Directive that references an API object."""

    api_object: ApiObject

    @property
    def object_path(self) -> ObjectPath:
        """Get the object path from the API object."""
        return self.api_object.object_path

    @property
    def object_type(self) -> DirectiveType:
        """Get the object type from the API object."""
        return self.api_object.object_type

    def symbol_name(self) -> str:
        """Get the symbol name from the API object."""
        return self.api_object.symbol_name

    def __str__(self) -> str:
        return f"::: {self.object_path}  # {self.object_type.value}"

    def render(self, current_docs_path: str) -> str:
        """Render directive as JSX-like component for debugging.

        Args:
            current_docs_path: The docs path of the current page (e.g., "calls" or "index")

        Returns:
            Either a simple path reference or full ApiObject depending on whether
            this is the canonical location for the object.

        """
        if self.api_object.canonical_docs_path == current_docs_path:
            # This is the canonical location - render full ApiObject
            return f'<ApiObject\n  path="{self.api_object.object_path}"\n  symbolName="{self.api_object.symbol_name}"\n  slug="{self.api_object.canonical_slug}"\n  canonicalPath="{self.api_object.canonical_docs_path}"\n/>'
        else:
            # This is just a reference - render simple path
            return f'<Directive path="{self.api_object.object_path}" />'


@dataclass
class DirectivesPage:
    """Enriched directives page with computed file path and enriched directives."""

    raw_page: RawDirectivesPage
    directives: list[Directive]

    @property
    def directory(self) -> str:
        """Get the directory from the underlying raw page."""
        return self.raw_page.directory

    @property
    def slug(self) -> Slug:
        """Get the slug from the underlying raw page."""
        return self.raw_page.slug

    @property
    def name(self) -> str:
        """Get the name from the underlying raw page."""
        return self.raw_page.name

    @property
    def file_path(self) -> str:
        """Get the full file path with .mdx extension."""
        return self.raw_page.file_path


class ApiDocumentation:
    """Container for all API documentation with global symbol resolution.

    This class wraps a list of DirectivesPage objects and provides:
    - Global symbol registry for conflict resolution
    - Canonical vs alias assignment
    - Symbol-level slug resolution
    - Canonical docs path mapping for cross-references
    """

    def __init__(self, raw_pages: list[RawDirectivesPage], api_root: str) -> None:
        # Validate unique file paths
        file_paths = set()
        for page in raw_pages:
            if page.file_path in file_paths:
                raise ValueError(f"Duplicate file path: {page.file_path}")
            file_paths.add(page.file_path)

        self.raw_pages = raw_pages
        self.api_root = api_root
        self._api_objects_registry = self._build_api_objects_registry()
        self._build_symbol_registry()
        self.pages = self._build_enriched_pages()
        # Track symbols that we can't find URLs for
        self._unresolved_symbols: set[str] = set()

    def _build_api_objects_registry(self) -> dict[ObjectPath, ApiObject]:
        """Build a registry of all API objects with their canonical properties.

        Uses conflict resolution to ensure unique slugs and first encounter for canonical docs path.
        Starts by adding builtin Python types, then adds package-specific types.

        Returns:
            Dictionary mapping ObjectPath -> ApiObject

        """
        registry: dict[ObjectPath, ApiObject] = {}
        used_slugs: dict[str, ObjectPath] = {}

        # First, add builtin Python types from type_urls.py
        for type_name, doc_url in BUILTIN_TYPE_URLS.items():
            # Create ApiObject for builtin type
            base_slug = self._camel_to_kebab(type_name)
            api_object = ApiObject(
                object_path=ObjectPath(type_name),
                object_type=DirectiveType.ALIAS,  # Treat as external alias
                canonical_slug=Slug(base_slug),
                canonical_docs_path=doc_url,  # Use the full external URL as the path
                symbol_name=type_name,
            )
            registry[ObjectPath(type_name)] = api_object
            used_slugs[base_slug] = ObjectPath(type_name)

        # Type suffix mappings for disambiguation
        type_suffixes = {
            DirectiveType.FUNCTION: "fn",
            DirectiveType.CLASS: "cls",
            DirectiveType.MODULE: "mod",
            DirectiveType.ALIAS: "alias",
            DirectiveType.ATTRIBUTE: "attr",
        }

        for page in self.raw_pages:
            # Get docs path without .mdx extension for canonical docs path
            docs_path = page.file_path.replace(".mdx", "")

            for directive in page.directives:
                # Check if we already have this object
                if directive.object_path in registry:
                    # Update canonical docs path if this one is deeper (more specific)
                    existing_api_object = registry[directive.object_path]
                    current_depth = (
                        0 if docs_path == "index" else 1 + docs_path.count("/")
                    )
                    existing_depth = (
                        0
                        if existing_api_object.canonical_docs_path == "index"
                        else 1 + existing_api_object.canonical_docs_path.count("/")
                    )
                    if current_depth > existing_depth:
                        existing_api_object.canonical_docs_path = docs_path
                    continue

                # Get the symbol name
                symbol_name = directive.symbol_name()
                # Convert camelCase/PascalCase to kebab-case for readability
                base_slug = self._camel_to_kebab(symbol_name)

                # Find unique slug using conflict resolution
                final_slug_str = base_slug
                if base_slug in used_slugs:
                    # Try with type suffix
                    type_suffix = type_suffixes.get(directive.object_type, "unknown")
                    typed_slug = f"{base_slug}_{type_suffix}"

                    if typed_slug not in used_slugs:
                        final_slug_str = typed_slug
                    else:
                        # Try with numbered suffix
                        counter = 1
                        while True:
                            numbered_slug = f"{typed_slug}_{counter}"
                            if numbered_slug not in used_slugs:
                                final_slug_str = numbered_slug
                                break
                            counter += 1

                # Create the ApiObject
                api_object = ApiObject(
                    object_path=directive.object_path,
                    object_type=directive.object_type,
                    canonical_slug=Slug(final_slug_str),
                    canonical_docs_path=docs_path,
                    symbol_name=symbol_name,
                )

                # Register it
                registry[directive.object_path] = api_object
                used_slugs[final_slug_str] = directive.object_path

        return registry

    def _build_symbol_registry(self) -> None:
        """Build a registry mapping symbol names to their canonical API objects.

        Stores unique symbols in self._symbol_registry and conflicts in self._orphaned_objects.
        """
        symbol_registry: dict[str, ApiObject] = {}
        symbol_conflicts: dict[str, list[ApiObject]] = {}

        # Collect all symbols and track conflicts
        for api_object in self._api_objects_registry.values():
            symbol_name = api_object.symbol_name

            if symbol_name in symbol_registry:
                # This is a conflict - move to conflicts tracking
                if symbol_name not in symbol_conflicts:
                    # First time seeing this conflict - move the original to conflicts too
                    symbol_conflicts[symbol_name] = [symbol_registry[symbol_name]]
                    del symbol_registry[symbol_name]

                symbol_conflicts[symbol_name].append(api_object)
            elif symbol_name not in symbol_conflicts:
                # No conflict yet, add to registry
                symbol_registry[symbol_name] = api_object

        # Store results on instance
        self._symbol_registry = symbol_registry
        self._overloaded_symbols = symbol_conflicts

    def _camel_to_kebab(self, name: str) -> str:
        """Convert camelCase/PascalCase to kebab-case."""
        # Insert hyphens before uppercase letters (except at start)
        result = re.sub(r"(?<!^)(?=[A-Z])", "-", name)
        return result.lower()

    def get_api_object(self, object_path: ObjectPath) -> ApiObject:
        """Get the API object for a given object path.

        Args:
            object_path: The canonical object path (e.g., "mirascope_v2_llm.calls.decorator.call")

        Returns:
            The ApiObject for this path

        Raises:
            ValueError: If no ApiObject is found for the given path

        """
        api_object = self._api_objects_registry.get(object_path)
        if api_object is None:
            raise ValueError(f"No API object found for path: {object_path}")
        return api_object

    def _build_enriched_pages(self) -> list[DirectivesPage]:
        """Build enriched pages with computed slugs.

        Returns:
            List of enriched DirectivesPage objects

        """
        enriched_pages = []

        for raw_page in self.raw_pages:
            enriched_directives = []

            for raw_directive in raw_page.directives:
                # Get the API object for this directive
                api_object = self.get_api_object(raw_directive.object_path)

                # Create enriched directive
                enriched_directive = Directive(api_object=api_object)
                enriched_directives.append(enriched_directive)

            # Create enriched page
            enriched_page = DirectivesPage(
                raw_page=raw_page, directives=enriched_directives
            )
            enriched_pages.append(enriched_page)

        return enriched_pages

    def generate_symbols_debug(self) -> str:
        """Generate debug output showing all unique symbols in the registry.

        Returns:
            Markdown content for _symbols.md file

        """
        lines = ["# Symbol Registry", ""]

        for symbol_name in sorted(self._symbol_registry.keys()):
            api_object = self._symbol_registry[symbol_name]
            canonical_file_path = f"{api_object.canonical_docs_path}.mdx"
            lines.append(
                f'<SymbolRef name="{symbol_name}" path="{canonical_file_path}" />'
            )
            lines.append("")

        return "\n".join(lines)

    def generate_overloaded_debug(self) -> str | None:
        """Generate debug output showing all overloaded symbols (conflicts).

        Returns:
            Markdown content for _overloaded.md file, or None if no overloaded symbols

        """
        if not self._overloaded_symbols:
            return None

        lines = ["# Overloaded Symbols", ""]
        lines.append(
            "These symbols appear in multiple objects and cannot be uniquely resolved:"
        )
        lines.append("")

        for symbol_name in sorted(self._overloaded_symbols.keys()):
            conflicting_objects = self._overloaded_symbols[symbol_name]
            lines.append(f"## {symbol_name}")
            lines.append("")

            for api_object in conflicting_objects:
                canonical_file_path = f"{api_object.canonical_docs_path}.mdx"
                lines.append(
                    f'<SymbolRef name="{symbol_name}" path="{canonical_file_path}" objectPath="{api_object.object_path}" />'
                )

            lines.append("")

        return "\n".join(lines)

    def __iter__(self) -> Iterator[DirectivesPage]:
        """Allow iteration over pages."""
        return iter(self.pages)

    def __len__(self) -> int:
        """Return number of pages."""
        return len(self.pages)

    def get_slug(self, object_path: ObjectPath) -> Slug:
        """Get a slug for an object path.

        If the object path exists in the API registry, return its canonical slug.
        Otherwise, generate a slug by converting the path (replace dots with hyphens and apply kebab-case).

        Args:
            object_path: The object path to get a slug for

        Returns:
            A unique slug for the object

        """
        # First try to get it from the API registry
        if object_path in self._api_objects_registry:
            return self._api_objects_registry[object_path].canonical_slug

        # Otherwise, generate a slug from the path
        # Replace dots with hyphens and apply kebab-case conversion
        path_str = str(object_path).replace(".", "-")
        kebab_path = self._camel_to_kebab(path_str)
        return Slug(kebab_path)

    def print_unresolved_symbols(self) -> None:
        """Print all symbols that could not be resolved to URLs."""
        if not self._unresolved_symbols:
            print("✅ All symbols resolved successfully!")
            return

        print(f"\n⚠️  Found {len(self._unresolved_symbols)} unresolved symbols:")
        for symbol in sorted(self._unresolved_symbols):
            print(f"  - {symbol}")
        print()

    @classmethod
    def from_module(cls, module: Module, api_root: str) -> "ApiDocumentation":
        """Discover API directives with hierarchical organization.

        This creates a structure like:
        - index.mdx (main module with its exports)
        - submodule.mdx (submodule with its exports)
        - nested/submodule.mdx (nested submodules)

        Args:
            module: The loaded Griffe module to analyze
            api_root: The root path for API documentation URLs

        Returns:
            ApiDocumentation object containing all pages with symbol registry

        """
        # Use the new recursive discovery function
        pages = discover_module_pages(module)

        return cls(pages, api_root)


def _resolve_member(module: Module, name: str) -> Object | Alias:
    """Resolve a member name, prioritizing imports over submodules for name conflicts."""
    # Try custom import resolution first
    if hasattr(module, "imports") and name in module.imports:
        import_path = module.imports[name]

        # Determine the base module for resolution
        if import_path.startswith("."):
            # Relative import - use current module as base
            base_module = module
        else:
            # Absolute import - use root module as base
            base_module = module
            while base_module.parent is not None:
                parent = base_module.parent
                if isinstance(parent, Module):
                    base_module = parent
                else:
                    break

        member = _resolve_import_path(import_path, base_module)
        if member is not None:
            return member

    # Fall back to normal resolution
    try:
        return module[name]
    except Exception:
        return module.members[name]


def _resolve_import_path(
    import_path: str, root_module: Module
) -> Object | Alias | None:
    """Recursive import resolution with final-step import prioritization.

    This allows us to correctly resolve "shadowed imports" despite an underlying bug in
    Griffe. Consider the case with imports like:
    from .call import Call
    from .decorator import call

    The call symbol resolves to a function from decorator.py, but Griffe will try to resolve
    it to the module corresponding to call.py.

    So instead we resolve it by checking the imports. However, we only do this on the last
    step. That way if we have the following situation:

    from .calls import call, Call

    When Call resolves to .calls.call.Call, we do not want the middle step in resolution
    to get the decorator - in that case we really do want to step into the call.py module
    and find Call
    """
    parts = import_path.split(".")
    current = root_module

    # Skip the root module name if it matches the first part
    start_index = 0
    if parts[0] == current.name:
        start_index = 1

    # Navigate down the path
    for i in range(start_index, len(parts)):
        part = parts[i]
        is_final_step = i == len(parts) - 1

        if is_final_step:
            # Final step: prioritize imports (the actual target we want)
            if hasattr(current, "imports") and part in current.imports:
                nested_import_path = current.imports[part]
                return _resolve_import_path(nested_import_path, root_module)

            # Fall back to members for final step
            if hasattr(current, "members") and part in current.members:
                current = current.members[part]
            else:
                return None
        # Intermediate step: prioritize members (navigation through module structure)
        elif hasattr(current, "members") and part in current.members:
            current = current.members[part]
        else:
            return None

    return current


def _extract_all_exports(module: Module) -> list[str] | None:
    """Extract __all__ exports from a Griffe module.

    Args:
        module: The module to analyze

    Returns:
        List of export names if __all__ is defined, None otherwise

    """
    if "__all__" not in module.members:
        # Fallback to public members (no hacky filtering)
        fallback_exports = []
        for name, member in module.members.items():
            # Skip private members
            if name.startswith("_"):
                continue

            # Include classes, functions, modules, and attributes
            if isinstance(member, Class | Function | Module | Attribute):
                fallback_exports.append(name)

        return fallback_exports

    all_member = module.members["__all__"]

    # Use getattr to safely access the value attribute
    value = getattr(all_member, "value", None)
    if value is None:
        return None

    # If it's a Griffe ExprList, extract the elements
    elements = getattr(value, "elements", None)
    if elements is not None:
        exports = []
        for elem in elements:
            elem_value = getattr(elem, "value", None)
            if elem_value is not None:
                clean_name = str(elem_value).strip("'\"")
                exports.append(clean_name)
            else:
                exports.append(str(elem).strip("'\""))
        return exports
    # If it's already a list, use it
    elif isinstance(value, list):
        return [str(item).strip("'\"") for item in value]
    # If it's a string representation, try to safely evaluate it
    elif isinstance(value, str):
        import ast

        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return None

    return None


def _create_directive_from_member(member: Object | Alias) -> RawDirective:
    """Create a Directive from a Griffe member object.

    Args:
        member: The Griffe object to create a directive for

    Returns:
        Directive object with appropriate type and path

    """
    if isinstance(member, Class):
        return RawDirective(ObjectPath(member.canonical_path), DirectiveType.CLASS)
    elif isinstance(member, Function):
        return RawDirective(ObjectPath(member.canonical_path), DirectiveType.FUNCTION)
    elif isinstance(member, Module):
        return RawDirective(ObjectPath(member.canonical_path), DirectiveType.MODULE)
    elif isinstance(member, Attribute):
        return RawDirective(ObjectPath(member.canonical_path), DirectiveType.ATTRIBUTE)
    elif isinstance(member, Alias):
        # Handle aliases - use the target's type instead of ALIAS
        target = member.target
        if isinstance(target, Class):
            directive_type = DirectiveType.CLASS
        elif isinstance(target, Function):
            directive_type = DirectiveType.FUNCTION
        elif isinstance(target, Module):
            directive_type = DirectiveType.MODULE
        elif isinstance(target, Attribute):
            directive_type = DirectiveType.ATTRIBUTE
        else:
            directive_type = DirectiveType.ALIAS
        return RawDirective(ObjectPath(target.canonical_path), directive_type)
    else:
        # Debug output to see what type we're dealing with
        member_type = type(member).__name__
        member_class = member.__class__
        raise ValueError(
            f"Unknown directive type: {member.canonical_path} (type: {member_type}, class: {member_class})"
        )


def discover_module_pages(
    module: Module, base_path: str = ""
) -> list[RawDirectivesPage]:
    """Recursively discover pages for a module and its submodules.

    Args:
        module: The Module object to process
        base_path: The path prefix for nested modules (e.g., "calls" for submodules)

    Returns:
        List of DirectivesPage objects for this module and all submodules

    """
    if base_path:
        parts = base_path.split("/")
        directory = "/".join(parts[:-1]) if len(parts) > 1 else ""
        slug_name = parts[-1]
    else:
        directory = ""
        slug_name = "index"

    module_page = RawDirectivesPage(
        [], directory, Slug.from_name(slug_name), module.name
    )
    pages = [module_page]

    export_names = _extract_all_exports(module)

    if export_names is None:
        raise ValueError(f"Module {module.canonical_path} has no __all__")

    seen_exports: set[str] = set()

    for export_name in export_names:
        if export_name in seen_exports:
            print(
                f"⚠️  Warning: Module {module.canonical_path} has duplicate export in __all__: {export_name}"
            )
            continue
        seen_exports.add(export_name)
        if export_name not in module.members:
            raise ValueError(
                f"Export '{export_name}' in __all__ not found in module {module.canonical_path}"
            )

        member = _resolve_member(module, export_name)

        if isinstance(member, Module):
            # Skip private modules (starting with _)
            if export_name.startswith("_"):
                continue

            # This is a submodule - give it dedicated page(s) (recursive)
            submodule_base_path = (
                f"{base_path}/{export_name}" if base_path else export_name
            )
            submodule_pages = discover_module_pages(member, submodule_base_path)
            pages.extend(submodule_pages)

        # Add a directive to this module's page (including for submodules - will render a link)
        directive = _create_directive_from_member(member)
        module_page.directives.append(directive)

    return pages


def _collect_submodule_exports(
    module: Module, seen_paths: set[str] | None = None
) -> list[RawDirective]:
    """Collect all non-Module exports from a module (not recursive into submodules).

    Args:
        module: The Module object to process
        seen_paths: Set of already-seen object paths to avoid duplicates

    Returns:
        List of RawDirective for all non-Module exports

    """
    if seen_paths is None:
        seen_paths = set()

    directives: list[RawDirective] = []
    export_names = _extract_all_exports(module)

    if export_names is None:
        return directives

    for export_name in export_names:
        if export_name not in module.members:
            continue

        member = _resolve_member(module, export_name)

        # Skip modules - we only want the actual exports
        if isinstance(member, Module):
            continue

        # Create directive and add if not already seen
        directive = _create_directive_from_member(member)
        if directive.object_path not in seen_paths:
            seen_paths.add(directive.object_path)
            directives.append(directive)

    return directives


def discover_flat_export_pages(
    module: Module, product_slug: str
) -> list[RawDirectivesPage]:
    """Generate pages for each top-level submodule under a product directory.

    Each submodule (calls, content, messages, etc.) gets one page containing
    all of its exports. This keeps related items together on a single page.

    Args:
        module: The Module object to process
        product_slug: The product directory name (e.g., "llm")

    Returns:
        List of RawDirectivesPage objects with one page per submodule

    """
    pages: list[RawDirectivesPage] = []
    seen_paths: set[str] = set()

    export_names = _extract_all_exports(module)
    if export_names is None:
        return pages

    # Process each export - create pages for submodules
    for export_name in export_names:
        if export_name not in module.members:
            continue

        member = _resolve_member(module, export_name)

        if isinstance(member, Module):
            # Skip private modules
            if export_name.startswith("_"):
                continue

            # Collect all exports from this submodule
            submodule_directives = _collect_submodule_exports(member, seen_paths)

            if submodule_directives:
                # Create a page for this submodule with all its exports
                slug = Slug.from_name(export_name)
                page = RawDirectivesPage(
                    directives=submodule_directives,
                    directory=product_slug,
                    slug=slug,
                    name=export_name,
                )
                pages.append(page)

    return pages
