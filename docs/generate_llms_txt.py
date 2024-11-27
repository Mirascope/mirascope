import re
from pathlib import Path
from dataclasses import dataclass
from typing import Any
import yaml


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
    canonical_url: str  # Points to HTML version
    markdown_url: str  # Points to Markdown version
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

    def _get_urls(self, path: str) -> tuple[str, str]:
        """
        Generate both canonical (HTML) and markdown URLs for a given path.

        Returns:
            tuple[str, str]: (canonical_url, markdown_url)
        """
        # Handle external URLs
        if path.startswith(("http://", "https://")):
            return path, path

        # Strip file extension and ensure path starts without leading slash
        clean_path = path.replace(".md", "").replace(".ipynb", "").lstrip("/")

        # Special handling for index.md
        if path == "index.md":
            return f"{self.base_url}/", f"{self.base_url}/index.html.md"

        # For all other paths
        canonical_url = f"{self.base_url}/{clean_path}/"

        # Convert paths like "prompts/" to "prompts/index.html.md"
        if clean_path.endswith("/"):
            markdown_url = f"{self.base_url}/{clean_path}index.html.md"
        else:
            markdown_url = f"{self.base_url}/{clean_path}/index.html.md"

        return canonical_url, markdown_url

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
        Now includes both HTML and Markdown URLs.
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
            title = (
                parent_title
                or item.rsplit("/", 1)[-1].rsplit(".", 1)[0].replace("_", " ").title()
            )

            canonical_url, markdown_url = self._get_urls(item)

            result.append(
                NavItem(
                    path=item,
                    title=title,
                    section=section,
                    canonical_url=canonical_url,
                    markdown_url=markdown_url,
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
        Links to markdown version but includes canonical HTML URL in description.
        """
        return f"- [{item.title}]({item.markdown_url}): {item.description}"

    def _organize_sections(self, nav_items: list[NavItem]) -> dict[str, list[NavItem]]:
        """Organize nav items into core and optional sections"""
        sections = {section: [] for section in LLMsConfig.CORE_SECTIONS}
        sections["Optional"] = []

        for item in nav_items:
            section = self._get_section(item)
            sections[section].append(item)

        return {k: v for k, v in sections.items() if v}

    def generate_llms_txt(self) -> str:
        """Generate llms.txt content with proper sectioning and canonical URLs"""
        nav_items = self._get_nav_structure()
        sections = self._organize_sections(nav_items)

        content = [
            "# Mirascope",
            "",
            f"> {self.config.get('site_description')}",
            "",
        ]

        for section_name in LLMsConfig.CORE_SECTIONS:
            if section_name in sections and sections[section_name]:
                content.extend([f"## {section_name}", ""])
                content.extend(
                    self._format_link(item) for item in sections[section_name]
                )
                content.append("")

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
    """Main entry point for llms.txt generation"""
    try:
        project_root = Path(__file__).parent.parent

        generator = LLMsGenerator(
            mkdocs_yml_path=project_root / "mkdocs.yml", description_map=description_map
        )

        output_path = generator.write_llms_txt()
        print(f"Successfully generated llms.txt at {output_path}")

    except Exception as e:
        print(f"Error generating llms.txt: {e}")
        raise


if __name__ == "__main__":
    main()
