"""Documentation generation tools for API reference documentation.

This module provides a DocumentationGenerator class that handles generating API
documentation from source repositories by extracting docstrings and processing
API directives using Griffe.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from api2mdx.api_discovery import (
    ApiDocumentation,
    DirectivesPage,
    discover_flat_export_pages,
    discover_internal_export_pages,
)
from api2mdx.griffe_integration import get_loader, render_directive
from api2mdx.meta import (
    DocSpec,
    ProductSpec,
    SectionSpec,
    generate_meta_file_content,
    generate_meta_from_directives,
)


class DocumentationGenerator:
    """Handles the generation of API documentation from source repositories.

    This class encapsulates the entire documentation generation process, including:
    - Loading the module with Griffe
    - Processing API documentation files
    - Generating formatted MDX output
    """

    source_path: Path
    """Path to the source code directory."""

    api_root: str
    """Root route for links to api docs (e.g. /docs/mirascope/api)."""

    package: str
    """Python package name to document."""

    docs_path: str
    """Path within the package where docs are located."""

    output_path: Path
    """Path where generated documentation should be written."""

    module: Any | None
    """Loaded Griffe module, or None if not yet loaded."""

    api_documentation: ApiDocumentation | None
    """Discovered API documentation, or None if not yet discovered."""

    product_slug: str
    """Product slug for documentation (e.g., 'llm')."""

    product_label: str
    """Product label for documentation (e.g., 'LLM')."""

    append_mode: bool
    """Whether to append to existing output instead of clearing it."""

    internal_structure: bool
    """Whether to discover structure from _internal imports in __init__.py."""

    def __init__(
        self,
        *,
        source_path: Path,
        package: str,
        docs_path: str,
        output_path: Path,
        api_root: str,
        product_slug: str,
        product_label: str,
        append_mode: bool = False,
        internal_structure: bool = False,
    ) -> None:
        """Initialize the DocumentationGenerator.

        Args:
            source_path: Path to the source code directory
            package: Python package name to document
            docs_path: Path within the package where docs are located
            output_path: Path where generated documentation should be written
            api_root: Root route for links to api docs (e.g. /docs/mirascope/api)
            product_slug: Product slug for documentation (e.g., 'llm')
            product_label: Product label for documentation (e.g., 'LLM')
            append_mode: Whether to append to existing output instead of clearing it
            internal_structure: Whether to discover structure from _internal imports

        """
        self.source_path = source_path
        self.api_root = api_root
        self.package = package
        self.docs_path = docs_path
        self.output_path = output_path
        self.module = None
        self.api_documentation = None
        self.product_slug = product_slug
        self.product_label = product_label
        self.append_mode = append_mode
        self.internal_structure = internal_structure

    def generate_all(self, directive_output_path: Path | None = None) -> None:
        """Generate all documentation files.

        Args:
            directive_output_path: Optional path to output intermediate directive files

        """
        # Load the module
        self.module = self._load_module()

        # Discover API directives from module structure
        if self.module is None:
            raise RuntimeError("Module must be loaded before discovering directives")

        if self.internal_structure:
            # Use internal structure discovery (parses from ._internal.X imports)
            raw_pages = discover_internal_export_pages(self.module, self.product_slug)
            self.api_documentation = ApiDocumentation(raw_pages, self.api_root)
            print(
                f"Discovered {len(self.api_documentation)} API directives (internal structure under {self.product_slug}/)"
            )
        else:
            # Use flat structure discovery (default)
            raw_pages = discover_flat_export_pages(self.module, self.product_slug)
            self.api_documentation = ApiDocumentation(raw_pages, self.api_root)
            print(
                f"Discovered {len(self.api_documentation)} API directives under {self.product_slug}/"
            )

        # Output directive snapshots if requested
        if directive_output_path:
            self.output_directive_snapshots(directive_output_path)

        # Clear target directory if it exists (unless in append mode)
        if not self.append_mode and self.output_path.exists():
            shutil.rmtree(self.output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Generate files from discovered directives
        for api_directive in self.api_documentation:
            self.generate_directive(api_directive)

        # Generate metadata
        self._generate_meta_file()

        # Print any unresolved symbols for debugging
        self.api_documentation.print_unresolved_symbols()

    def generate_directive(self, api_directive: DirectivesPage) -> None:
        """Generate documentation for a specific directive.

        Args:
            api_directive: The ApiDirective object containing directive string and output path

        """
        if not self.module:
            raise RuntimeError("Setup must be called before generating documentation")

        try:
            target_path = self.output_path / api_directive.file_path

            # Ensure target directory exists
            target_path.parent.mkdir(exist_ok=True, parents=True)

            # Process directive
            self._write_directives_page(api_directive)
        except Exception as e:
            print(f"ERROR: Failed to process directive {api_directive.directives}: {e}")
            # Re-raise the exception to maintain the original behavior
            raise

    def output_directive_snapshots(self, directive_output_path: Path) -> None:
        """Output directives as intermediate .md files for debugging/inspection.

        Args:
            directive_output_path: Path where directive files should be written

        """
        if not self.api_documentation:
            raise RuntimeError("API directives must be discovered before output")

        # Clear and create directive output directory
        if directive_output_path.exists():
            shutil.rmtree(directive_output_path)
        directive_output_path.mkdir(parents=True, exist_ok=True)

        for api_directive in self.api_documentation:
            # Get docs path for this directive page (without .mdx extension)
            docs_path = api_directive.file_path.replace(".mdx", "")
            directive_content = f"# {api_directive.name}\n\n" + "\n\n".join(
                directive.render(docs_path) for directive in api_directive.directives
            )

            # Write to .md file in directive output directory
            directive_file_path = (
                directive_output_path / api_directive.file_path.replace(".mdx", ".md")
            )
            directive_file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(directive_file_path, "w") as f:
                f.write(directive_content)

        # Generate debug files for symbol registry
        symbols_debug = self.api_documentation.generate_symbols_debug()
        symbols_file_path = directive_output_path / "_symbols.md"
        with open(symbols_file_path, "w") as f:
            f.write(symbols_debug)

        # Generate debug file for overloaded symbols if any exist
        overloaded_debug = self.api_documentation.generate_overloaded_debug()
        if overloaded_debug:
            overloaded_file_path = directive_output_path / "_overloaded.md"
            with open(overloaded_file_path, "w") as f:
                f.write(overloaded_debug)

        print(
            f"Generated {len(self.api_documentation)} directive files in {directive_output_path}"
        )

    def _load_module(self) -> Any:  # noqa: ANN401
        """Load the module using Griffe.

        Returns:
            Loaded Griffe module

        """
        try:
            # Add source path to sys.path temporarily
            sys.path.insert(0, str(self.source_path))

            # Load the module with basic loader
            loader = get_loader()

            # Try to preload common external dependencies to improve alias resolution
            common_dependencies = [
                "collections.abc",
                "typing",
                "openai",
                "mistralai",
                "functools",
                "base64",
                "typing_extensions",
                "__future__",
            ]
            for dep in common_dependencies:
                try:
                    loader.load(dep)
                    print(f"Preloaded {dep} for alias resolution")
                except Exception as e:
                    print(f"Info: {dep} preload skipped: {e}")

            # Load the main module
            module = loader.load(self.package)

            # Handle alias resolution errors gracefully
            try:
                loader.resolve_aliases(external=True)
            except Exception as e:
                print(f"Warning: Some aliases could not be resolved: {e}")
                print("Documentation generation will continue despite this warning.")

            print(f"Loaded module {self.package}")
            return module
        finally:
            # Clean up sys.path
            if str(self.source_path) in sys.path:
                sys.path.remove(str(self.source_path))

    def _write_directives_page(self, directives_page: DirectivesPage) -> None:
        """Process directives and generate the corresponding MDX file.

        Args:
            api_directive: The ApiDirective object containing directives and output info

        """
        if not self.module:
            raise RuntimeError("Module must be loaded before processing directives")

        # Get target path from the directive's slug
        target_path = self.output_path / directives_page.file_path

        # Extract title from directive name
        title = directives_page.name

        # Get the relative file path for the API component
        relative_path = target_path.relative_to(self.output_path)
        doc_path = str(relative_path.with_suffix(""))  # Remove .mdx extension

        # Write the target file with frontmatter and processed content
        with open(target_path, "w") as f:
            f.write("---\n")
            # Add auto-generation notice as a comment in the frontmatter
            f.write("# AUTO-GENERATED API DOCUMENTATION - DO NOT EDIT\n")
            f.write(f"title: {title}\n")
            f.write(f"description: API documentation for {title}\n")
            f.write("---\n\n")
            f.write(f"# {title}\n\n")

            # Process each directive
            for directive in directives_page.directives:
                # Create a RawDirective from the ApiObject for rendering
                from api2mdx.api_discovery import RawDirective

                raw_directive = RawDirective(
                    object_path=directive.api_object.object_path,
                    object_type=directive.api_object.object_type,
                )
                if not self.api_documentation:
                    raise RuntimeError(
                        "API documentation must be initialized before processing directives"
                    )
                doc_content = render_directive(
                    raw_directive, self.module, doc_path, self.api_documentation
                )
                f.write(doc_content)
                f.write("\n\n")

    def _generate_meta_file(self) -> None:
        """Generate metadata file and format it with prettier."""
        if not self.api_documentation:
            raise RuntimeError(
                "API directives must be discovered before generating metadata"
            )

        meta_path = self.output_path / "_meta.ts"

        # In append mode, merge with existing meta file
        if self.append_mode and meta_path.exists():
            content = self._merge_meta_file(meta_path)
        else:
            products = [ProductSpec(slug=self.product_slug, label=self.product_label)]

            api_section = generate_meta_from_directives(
                self.api_documentation.pages, weight=None, products=products
            )
            content = generate_meta_file_content(api_section)

        # Write to file
        with open(meta_path, "w") as f:
            f.write(content)
        print(f"Generated API meta file at {meta_path}")

        # Run prettier to format the file
        try:
            subprocess.run(
                ["bun", "prettier", "--write", str(meta_path)],
                check=True,
                capture_output=True,
            )
            print(f"Generated and formatted API meta file at {meta_path}")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Prettier formatting failed: {e}")
            print(f"Generated unformatted API meta file at {meta_path}")

    def _merge_meta_file(self, meta_path: Path) -> str:
        """Merge new product into existing meta file.

        Args:
            meta_path: Path to existing _meta.ts file

        Returns:
            Updated meta file content

        """
        if not self.api_documentation:
            raise RuntimeError("API documentation must be initialized before merging")

        # Read existing meta file
        with open(meta_path) as f:
            existing_content = f.read()

        # Extract existing products array using regex
        # Match the products array more flexibly (handles formatting with/without quotes)
        products_match = re.search(
            r"products:\s*\[([\s\S]*?)\],",
            existing_content,
        )
        existing_products: list[ProductSpec] = []
        if products_match:
            products_str = products_match.group(1)
            # Parse individual product objects - handle both quoted and unquoted keys
            # Match: { slug: "value", label: "value" } with flexible spacing
            product_matches = re.findall(
                r'\{\s*slug:\s*["\']([^"\']+)["\'],\s*label:\s*["\']([^"\']+)["\'],?\s*\}',
                products_str,
            )
            for slug, label in product_matches:
                existing_products.append(ProductSpec(slug, label))

        # Extract existing children array using regex
        # Find the main children array (first level)
        # The pattern matches children: [ ... ], }; followed by export
        # Using greedy matching anchored to the export statement
        children_match = re.search(
            r"children:\s*\[\s*(\{.*)\s*\],\s*\};\s*\nexport",
            existing_content,
            re.DOTALL,
        )
        existing_children: list[DocSpec] = []
        if children_match:
            children_str = children_match.group(1)
            # Parse each top-level child object
            # Find balanced braces for each child
            depth = 0
            start = 0
            for i, char in enumerate(children_str):
                if char == "{":
                    if depth == 0:
                        start = i
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        child_str = children_str[start : i + 1]
                        # Extract slug and label
                        slug_match = re.search(r'slug:\s*["\'](\w+)["\']', child_str)
                        label_match = re.search(
                            r'label:\s*["\']([^"\']+)["\']', child_str
                        )
                        if slug_match and label_match:
                            # Extract nested children if present
                            nested_children: list[DocSpec] | None = None
                            nested_children_match = re.search(
                                r"children:\s*\[(.*)\]", child_str, re.DOTALL
                            )
                            if nested_children_match:
                                nested_str = nested_children_match.group(1)
                                nested_children = []
                                # Match nested child objects with optional trailing commas
                                nested_matches = re.findall(
                                    r'\{\s*slug:\s*["\']([^"\']+)["\'],\s*label:\s*["\']([^"\']+)["\'],?\s*\}',
                                    nested_str,
                                )
                                for ns, nl in nested_matches:
                                    nested_children.append(DocSpec(slug=ns, label=nl))
                            existing_children.append(
                                DocSpec(
                                    slug=slug_match.group(1),
                                    label=label_match.group(1),
                                    children=nested_children,
                                )
                            )

        # Add new product if not already present
        new_product = ProductSpec(self.product_slug, self.product_label)
        if not any(p.slug == self.product_slug for p in existing_products):
            existing_products.append(new_product)

        # Generate new children from current api_documentation
        new_section = generate_meta_from_directives(
            self.api_documentation.pages, weight=None, products=None
        )

        # The new_section is a SectionSpec with children - find the child matching our product
        # generate_meta_from_directives builds a tree from file paths, so for ops/tracing.mdx
        # it produces children=[DocSpec(slug="ops", children=[DocSpec(slug="tracing"), ...])]
        # Find the child that matches our product slug
        product_child = None
        for child in new_section.children:
            if child.slug == self.product_slug:
                product_child = child
                break

        if product_child:
            # Use the existing structure from generate_meta_from_directives
            new_child_entry = product_child
        else:
            # Fallback: wrap children directly (shouldn't normally happen)
            new_child_entry = DocSpec(
                slug=self.product_slug,
                label=self.product_label,
                children=list(new_section.children),
            )

        # Replace or add the child for this product
        found = False
        for i, child in enumerate(existing_children):
            if child.slug == self.product_slug:
                existing_children[i] = new_child_entry
                found = True
                break
        if not found:
            existing_children.append(new_child_entry)

        # Generate the merged content
        merged_section = SectionSpec(
            slug="api",
            label="API Reference",
            children=existing_children,
            products=existing_products,
        )
        return generate_meta_file_content(merged_section)
