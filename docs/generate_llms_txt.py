import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import nbconvert
import yaml
from jinja2 import Environment, FileSystemLoader


class CodeBlockExpander:
    """Handles Python code block expansion in markdown files"""

    @staticmethod
    def parse_code_reference(
        code_path: str,
    ) -> tuple[str, tuple[int | None, int | None]]:
        """
        Parse code path and extract line specifications.
        Returns:
            tuple of (file_path, (start_line, end_line)) where:
            - start_line: line to start from (or None if not specified)
            - end_line: line to end at (or None if not specified)

        Examples:
            file.md -> (file.md, (None, None))
            file.md:3 -> (file.md, (3, None))
            file.md::3 -> (file.md, (1, 3))
            file.md:4:6 -> (file.md, (4, 6))
            file.md:29: -> (file.md, (29, None))  # New format support
        """
        parts = code_path.split(":")

        if len(parts) == 1:
            # No line specifications
            return code_path, (None, None)

        file_path = parts[0]
        if len(parts) == 2:
            # Single number format
            try:
                line_num = int(parts[1])
                return file_path, (line_num, None)
            except ValueError:
                return code_path, (None, None)

        if len(parts) == 3:
            try:
                if not parts[1] and parts[2]:  # file.md::3 format
                    end_line = int(parts[2])
                    return file_path, (1, end_line)
                elif parts[1] and not parts[2]:  # file.md:29: format
                    start_line = int(parts[1])
                    return file_path, (start_line, None)
                else:  # file.md:4:6 format
                    start_line = int(parts[1])
                    end_line = int(parts[2])
                    return file_path, (start_line, end_line)
            except ValueError:
                return code_path, (None, None)

        return code_path, (None, None)

    @staticmethod
    def get_line_range(code_path: str) -> tuple[str, tuple[int, int] | None]:
        """Parse code path and extract line range if specified."""
        if ":" not in code_path:
            return code_path, None

        parts = code_path.split(":")
        if len(parts) != 3:
            return code_path, None

        try:
            file_path = parts[0]
            start_line = int(parts[1])
            end_line = int(parts[2])
            return file_path, (start_line, end_line)
        except ValueError:
            return code_path, None

    @staticmethod
    def expand_code_block(
        code_path: str, project_root: str = "", base_indent: str = ""
    ) -> str:
        """
        Reads and returns content of a Python code file.
        Supports line specifications:
        - file.md:3 - start from line 3
        - file.md::3 - lines 1-3
        - file.md:4:6 - lines 4-6
        - file.md:29: - start from line 29 to end
        """
        try:
            if code_path.startswith('"') and code_path.endswith('"'):
                code_path = code_path[1:-1]

            # Parse path and get line specifications
            file_path, (start_line, end_line) = CodeBlockExpander.parse_code_reference(
                code_path
            )

            # If project root is provided, make path absolute
            if project_root:
                file_path = os.path.normpath(os.path.join(project_root, file_path))

            # Try both direct path and examples directory
            possible_paths = [
                file_path,
                os.path.join(project_root, "examples", file_path),
            ]

            content = None
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                        # Handle line specifications
                        if start_line is not None:
                            if end_line is not None:
                                # Both start and end specified
                                selected_lines = lines[start_line - 1 : end_line]
                            else:
                                # Only start specified - take all remaining lines
                                selected_lines = lines[start_line - 1 :]
                        elif end_line is not None:
                            # Only end specified (implied start from 1)
                            selected_lines = lines[:end_line]
                        else:
                            # No line specifications
                            selected_lines = lines

                        # Apply base indentation plus 4 spaces for code block
                        indented_lines = [
                            f"{base_indent}    {line}" if line.strip() else line
                            for line in selected_lines
                        ]
                        content = "".join(indented_lines).rstrip()
                        break

            if content is not None:
                return content
            return f"{base_indent}    # Code file not found: {file_path}\n"

        except Exception as e:
            print(f"Error reading code file {code_path}: {e}")
            return f"{base_indent}    # Error reading code: {e}\n"


class JinjaRenderer:
    """Handles Jinja2 template rendering with MkDocs variables"""

    def __init__(self, config: dict, project_root: str):
        self.env = Environment(
            loader=FileSystemLoader("docs"),
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
        )
        self.project_root = project_root
        self._setup_environment(config)
        self._add_filters()

    def process_code_blocks(self, content: str) -> str:
        """Process code block inclusions in the rendered content"""
        lines = content.split("\n")
        result = []
        current_indent = ""

        for line in lines:
            # Update current indentation level
            if line.strip():
                current_indent = " " * (len(line) - len(line.lstrip()))

            # Look for code block inclusion
            match = re.search(r'--8<-- "([^"]+)"', line)
            if match:
                code_content = self.process_code_block_reference(match, current_indent)
                result.append(code_content)
            else:
                result.append(line)

        return "\n".join(result)

    def _setup_environment(self, config: dict):
        """Setup Jinja environment with MkDocs variables"""
        if "extra" in config:
            for key, value in config["extra"].items():
                self.env.globals[key] = value

        # Add built-in filters and functions
        def provider_dir(provider: str) -> str:
            """Convert provider name to directory name"""
            lower_provider = provider.lower()
            first_word = lower_provider.split()[0]
            return first_word

        self.env.filters["provider_dir"] = provider_dir
        self.env.globals["zip"] = zip

    def process_code_block_reference(self, match: re.Match, current_indent: str) -> str:
        """Process a single code block reference with template variables"""
        code_path = match.group(1)

        # First, expand any template variables in the path
        try:
            template = self.env.from_string(code_path)
            expanded_path = template.render()
        except Exception as e:
            print(f"Error expanding template variables in path '{code_path}': {e}")
            return f"{current_indent}    # Error expanding template variables: {e}"

        # Then read the code file with the expanded path
        return CodeBlockExpander.expand_code_block(
            expanded_path, self.project_root, current_indent
        )

    def _add_filters(self):
        """Add custom filters used in templates"""

        def provider_dir(provider: str) -> str:
            """
            Convert provider name to directory name.
            Special cases:
            - "Azure AI" -> "azure"
            - "Vertex AI" -> "vertex"
            """
            # Handle special cases first
            provider_mapping = {
                "Azure AI": "azure",
                "Vertex AI": "vertex",
            }

            if provider in provider_mapping:
                return provider_mapping[provider]

            # Default case: lowercase and take first word
            return provider.lower().split()[0]

        self.env.filters["provider_dir"] = provider_dir

    def render_template(
        self, template_content: str, extra_vars: dict | None = None
    ) -> str:
        """Render a template string with variables"""
        try:
            template = self.env.from_string(template_content)
            vars_dict = {}
            if extra_vars:
                vars_dict.update(extra_vars)
            return template.render(**vars_dict)
        except Exception as e:
            print(f"Error rendering template: {e}")
            return template_content


class MarkdownGenerator:
    """Generator for markdown files with Jinja2 template and code expansion support"""

    def __init__(self, mkdocs_yml_path: Path):
        """Initialize the generator"""
        self.mkdocs_yml_path = mkdocs_yml_path
        self.project_root = mkdocs_yml_path.parent
        self.config = self._load_config()
        self.jinja_renderer = JinjaRenderer(self.config, str(self.project_root))

    def _load_config(self) -> dict:
        """Load and validate mkdocs.yml configuration"""
        if not self.mkdocs_yml_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.mkdocs_yml_path}")

        def python_name_constructor(loader, suffix, node):
            return f"{suffix}.{node.value}"

        yaml.SafeLoader.add_multi_constructor(
            "tag:yaml.org,2002:python/name:", python_name_constructor
        )

        try:
            with open(self.mkdocs_yml_path) as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")

    def _get_output_path(self, input_path: Path) -> Path:
        """
        Generate the output path for a markdown file within docs directory
        """
        rel_path = input_path.relative_to("docs")

        # Handle index files
        if rel_path.name == "index.md":
            parent_dir = rel_path.parent
            return self.project_root / "docs" / parent_dir / "index.html.md"

        # Handle other markdown files - keep in docs directory
        stem = rel_path.stem
        parent_dir = rel_path.parent
        return self.project_root / "docs" / parent_dir / f"{stem}.html.md"

    def process_markdown_files(self, docs_dir: Path) -> None:
        """Process all markdown files in docs directory"""
        # Find all .md files but exclude .html.md files
        for markdown_file in docs_dir.rglob("*.md"):
            try:
                # Skip already processed .html.md files
                if markdown_file.name.endswith(".html.md"):
                    continue

                # Calculate output path in docs directory
                output_path = self._get_output_path(markdown_file)

                # Read markdown content
                content = markdown_file.read_text(encoding="utf-8")

                # Render Jinja templates in the content
                rendered_content = self.jinja_renderer.render_template(content)

                # Process code block inclusions
                final_content = self.jinja_renderer.process_code_blocks(
                    rendered_content
                )

                # Create output directory if it doesn't exist
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Write processed content
                output_path.write_text(final_content, encoding="utf-8")
                print(
                    f"Processed {markdown_file.relative_to(docs_dir)} -> {output_path.relative_to(self.project_root)}"
                )

            except Exception as e:
                print(f"Error processing {markdown_file}: {e}")

    def process_ipynb_files(self, docs_dir: Path) -> None:
        """Process all ipynb notebook files in docs directory"""
        for notebook_file in docs_dir.rglob("*.ipynb"):
            try:
                markdown_exporter = nbconvert.MarkdownExporter()
                output, _ = markdown_exporter.from_filename(
                    notebook_file.absolute().as_posix()
                )
                output_path = self._get_output_path(notebook_file)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(output)
                print(
                    f"Processed {notebook_file.relative_to(docs_dir)} -> {output_path.relative_to(self.project_root)}"
                )
            except Exception as e:
                print(f"Error processing {notebook_file}: {e}")

    def generate_markdown(self) -> None:
        """Generate markdown files with processed content directly in docs directory"""
        docs_dir = Path("docs")
        print(f"Processing markdown files in: {docs_dir}")
        self.process_markdown_files(docs_dir)
        self.process_ipynb_files(docs_dir)


class LLMsConfig:
    """Configuration constants for llms.txt generation"""

    CORE_SECTIONS = [
        "Essentials",
        "Core Features",
        "Provider Features",
        "Extensions",
        "Integrations",
    ]

    PATH_DESCRIPTION_TEMPLATES = {
        "learn/": "Learn about {} and how to use it effectively",
        "api/": "Complete API reference for {}",
        "tutorials/": "Step-by-step tutorial covering {}",
        "integrations/": "Integration guide for {}",
    }

    ESSENTIAL_PATHS = {"index.md", "WHY.md", "HELP.md", "MIGRATE.md", "CONTRIBUTING.md"}


# Default descriptions for essential pages
description_map = {
    "index.md": "Getting started with Mirascope's core concepts and installation",
    "WHY.md": "Key features and design philosophy behind Mirascope",
    "HELP.md": "Resources and guides for getting help with Mirascope",
    "MIGRATE.md": "Guide for migrating between Mirascope versions",
    "CONTRIBUTING.md": "Guidelines for contributing to Mirascope",
}


@dataclass
class NavItem:
    """Represents a navigation item with its metadata"""

    path: str
    title: str  # From mkdocs.yml
    section: str
    canonical_url: str
    description: str | None = None


class LLMsGenerator:
    """Generator for llms.txt files with SEO-friendly canonical URLs"""

    def __init__(
        self,
        mkdocs_yml_path: Path,
        base_url: str = "https://mirascope.com/docs",
        description_map: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize the generator
        Args:
            mkdocs_yml_path: Path to mkdocs.yml file
            base_url: Base URL for canonical links
            description_map: Optional mapping of paths to descriptions
        """
        self.mkdocs_yml_path = mkdocs_yml_path
        self.base_url = base_url.rstrip("/")
        self.description_map = description_map or {}
        self.config = self._load_config()

        # Validate config
        if not self.config.get("site_description"):
            raise ValueError("site_description is required in mkdocs.yml")

    def _load_config(self) -> dict:
        """Load and validate mkdocs.yml configuration"""
        if not self.mkdocs_yml_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.mkdocs_yml_path}")

        try:
            with open(self.mkdocs_yml_path) as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")

    def _get_canonical_url(self, path: str) -> str:
        """
        Generate canonical URL for a given path.
        Special cases:
        - index.md -> /docs/
        - other files -> /docs/path/
        """
        # First check if it's already a URL
        if path.startswith(("http://", "https://")):
            return path

        # Special handling for index.md
        if path == "index.md":
            return f"{self.base_url}/index.html.md"

        # Strip file extension and ensure path starts without leading slash
        path = path.replace(".md", "").replace(".ipynb", "").lstrip("/")

        # Add trailing slash if not present
        if not path.endswith("/"):
            path += "/"

        # Add .html.md extension
        path += "index.html.md"

        return f"{self.base_url}/{path}"

    def _get_description(self, path: str, title: str) -> str:
        """Get description for a path, falling back to generated description"""
        if path in self.description_map:
            return self.description_map[path]

        for prefix, template in LLMsConfig.PATH_DESCRIPTION_TEMPLATES.items():
            if path.startswith(prefix):
                clean_title = re.sub(r"[_\-]", " ", title).lower()
                return template.format(clean_title)

        return f"Documentation for {title}"

    def _get_section(self, item: NavItem) -> str:
        """Determine the section for a navigation item based on its path"""
        path = item.path
        if any(p in path for p in LLMsConfig.ESSENTIAL_PATHS):
            return "Essentials"

        section_map = {
            "learn/provider": "Provider Features",
            "learn/extensions": "Extensions",
            "learn/": "Core Features",
            "integrations/": "Integrations",
        }

        for prefix, section in section_map.items():
            if path.startswith(prefix):
                return section

        return "Optional"

    def _process_nav_item(
        self,
        item: Any,
        result: list[NavItem],
        section: str = "",
        parent_title: str = "",
    ) -> None:
        """
        Recursively process navigation items into NavItem objects.
        Extracts title from mkdocs.yml navigation structure.
        """
        if isinstance(item, dict):
            for title, content in item.items():
                if isinstance(content, list):
                    for sub_item in content:
                        self._process_nav_item(
                            sub_item, result, section or title, title
                        )
                else:
                    self._process_nav_item(content, result, section, title)
        elif isinstance(item, str) and (
            item.endswith(".md") or item.endswith(".ipynb")
        ):
            # Get the title from the navigation structure if available
            # Fall back to parent_title or clean path if not
            title = (
                parent_title
                or item.rsplit("/", 1)[-1].rsplit(".", 1)[0].replace("_", " ").title()
            )

            result.append(
                NavItem(
                    path=item,
                    title=title,
                    section=section,
                    canonical_url=self._get_canonical_url(item),
                    description=self._get_description(item, title),
                )
            )

    def _get_nav_structure(self) -> list[NavItem]:
        """Extract and organize navigation structure from mkdocs.yml"""
        result: list[NavItem] = []
        nav = self.config.get("nav", [])

        if not nav:
            raise ValueError("No navigation structure found in mkdocs.yml")

        for item in nav:
            self._process_nav_item(item, result)
        return result

    def _format_link(self, item: NavItem) -> str:
        """
        Format a navigation item as a markdown link.
        Both the link and canonical URL point to the generated HTML version.
        """
        return f"- [{item.title}]({item.canonical_url}): {item.description}"

    def _organize_sections(self, nav_items: list[NavItem]) -> dict[str, list[NavItem]]:
        """Organize nav items into core and optional sections"""
        sections = {section: [] for section in LLMsConfig.CORE_SECTIONS}
        sections["Optional"] = []  # Initialize Optional section

        for item in nav_items:
            section = self._get_section(item)
            sections[section].append(item)

        return {k: v for k, v in sections.items() if v}

    def generate_llms_txt(self) -> str:
        """Generate llms.txt content with proper sectioning and canonical URLs"""
        nav_items = self._get_nav_structure()
        sections = self._organize_sections(nav_items)

        # Build content
        content = [
            "# Mirascope",
            "",
            f"> {self.config.get('site_description')}",
            "",
        ]

        # Add core sections
        for section_name in LLMsConfig.CORE_SECTIONS:
            if section_name in sections and sections[section_name]:
                content.extend([f"## {section_name}", ""])
                content.extend(
                    self._format_link(item) for item in sections[section_name]
                )
                content.append("")

        # Add Optional section last
        if sections["Optional"]:
            content.extend(["## Optional", ""])
            content.extend(self._format_link(item) for item in sections["Optional"])
            content.append("")

        return "\n".join(content)

    def write_llms_txt(self, output_dir: Path | None = None) -> Path:
        """
        Generate and write llms.txt to specified directory
        Args:
            output_dir: Optional output directory (defaults to mkdocs docs directory)
        Returns:
            Path to generated llms.txt file
        """
        content = self.generate_llms_txt()

        if output_dir is None:
            output_dir = self.mkdocs_yml_path.parent / "docs"

        if not output_dir.exists():
            output_dir.mkdir(parents=True)

        output_path = output_dir / "llms.txt"
        output_path.write_text(content)
        return output_path


def main():
    """Main entry point"""
    try:
        project_root = Path(__file__).parent.parent
        mkdocs_yml_path = project_root / "mkdocs.yml"

        generator = MarkdownGenerator(mkdocs_yml_path=mkdocs_yml_path)
        generator.generate_markdown()
        print("Successfully generated markdown files in docs directory")

        generator = LLMsGenerator(
            mkdocs_yml_path=project_root / "mkdocs.yml", description_map=description_map
        )
        output_path = generator.write_llms_txt()
        print(f"Successfully generated llms.txt at {output_path}")

    except Exception as e:
        print(f"Error generating files: {e}")
        raise


if __name__ == "__main__":
    main()
