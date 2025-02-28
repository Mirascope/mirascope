import shutil
from pathlib import Path

from docs.generate_provider_examples import generate_provider_examples


def get_output_path(input_path: Path) -> Path:
    """
    Generate the output path for a markdown file.

    Args:
        input_path: Original markdown file path

    Returns:
        Path: Corresponding .html.md file path
    """
    rel_path = input_path.relative_to(input_path.parent.parent)
    stem = rel_path.stem
    if stem == "index":
        return input_path.parent.parent / "index.html.md"
    return input_path.parent / f"{stem}.html.md"


def copy_generated_html_md_files(markdown_dir: Path, site_dir: Path) -> None:
    """
    Copy generated .html.md files to their corresponding location in the site directory.
    Only copies files that have been processed by the markdown generator.

    Args:
        markdown_dir: Source directory containing markdown files (docs)
        site_dir: Output directory for the built site (site)
    """
    # for md_file in markdown_dir.rglob("*.md"):
    for html_md_file in markdown_dir.rglob("*.html.md"):
        # Skip already generated .html.md files
        # if md_file.name.endswith(".html.md"):
        #     continue

        # Get the path where the generated .html.md should be
        # html_md_file = get_output_path(md_file)

        # Only proceed if the .html.md file was actually generated
        # if not html_md_file.exists():
        # continue

        # Calculate relative path for site directory
        # rel_path = md_file.relative_to(markdown_dir)
        rel_path = html_md_file.relative_to(markdown_dir)
        parent_path = rel_path.parent
        base_name = rel_path.stem[: -len(".html")]

        # Construct destination path in site directory
        dest_dir = site_dir / parent_path
        if base_name != "index":
            dest_dir = dest_dir / base_name
        dest_path = dest_dir / "index.html.md"

        # Create destination directory if it doesn't exist
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Copy the file
        shutil.copy2(html_md_file, dest_path)
        print(f"Copied generated file: {html_md_file} to {dest_path}")


def on_post_build(config, **kwargs):
    """
    Hook that runs after the build is complete.
    Copy generated .html.md files to their corresponding locations in the site directory.
    """
    docs_dir = Path(config["docs_dir"])
    site_dir = Path(config["site_dir"])

    try:
        copy_generated_html_md_files(docs_dir, site_dir)
        print("Successfully copied generated .html.md files to site directory")
    except Exception as e:
        print(f"Error copying .html.md files: {e}")


def on_pre_build(config, **kwargs):
    """
    Hook that runs before the build.
    Generate provider specific examples.
    """

    try:
        example_dirs = config["extra"]["provider_example_dirs"]
        generate_provider_examples(
            example_dirs=example_dirs,
            examples_root=Path("examples"),
            snippets_dir=Path("build/snippets"),
        )
        print("Successfully generated provider examples")
    except Exception as e:
        print(f"Error generating provider examples: {e}")
        raise e
