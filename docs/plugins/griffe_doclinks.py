"""
Adapted from the Pydantic team's original script.
https://github.com/pydantic/pydantic/blob/main/docs/plugins/griffe_doclinks.py
"""

from __future__ import annotations

import ast
import logging
import re
import sys
import traceback
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from griffe import Extension, ObjectNode
from griffe import Object as GriffeObject
from pymdownx.slugs import slugify

DOCS_PATH = Path(__file__).parent.parent
slugifier = slugify(case="lower")
logger = logging.getLogger("griffe_doclinks")
logger.setLevel(logging.DEBUG)


def safe_regex_search(pattern: str, string: str, flags: int = 0) -> re.Match | None:
    try:
        return re.search(pattern, string, flags)
    except re.error as e:
        logger.error(f"Regex error with pattern '{pattern}': {str(e)}")
        return None


def find_heading(content: str, slug: str, file_path: Path) -> tuple[str, int]:
    results = safe_regex_search(r"^#+ (.+)", content, flags=re.M)
    for m in results or []:
        heading = m.group(1)
        h_slug = slugifier(heading, "-")
        if h_slug == slug:
            return heading, m.end()
    raise ValueError(f"heading with slug {slug!r} not found in {file_path}")


def get_local_api_link(obj_path: str) -> str:
    path_parts = obj_path.split(".")
    return f"/api/{'/'.join(path_parts)}"  # Remove '.md' and make it relative to root


def insert_or_update_api_section(file_path: Path, api_link: str, obj_path: str) -> None:
    try:
        content = file_path.read_text()
        api_section = (
            f'??? api "API Documentation"\n\n    [`{obj_path}`]({api_link})\n\n'
        )

        if '??? api "API Documentation"' in content:
            content = re.sub(
                r"??? api \"API Documentation\"\n\n.*?\n\n",
                api_section,
                content,
                flags=re.DOTALL,
            )
        else:
            first_heading_match = safe_regex_search(r"^# .+\n", content, re.MULTILINE)
            if first_heading_match:
                first_heading_end = first_heading_match.end()
                content = f"{content[:first_heading_end]}\n{api_section}{content[first_heading_end:]}"
            else:
                content = f"{api_section}{content}"

        file_path.write_text(content)
    except Exception:
        # logger.error(f"Error in insert_or_update_api_section: {str(e)}")
        logger.debug(traceback.format_exc())


def update_links(obj: GriffeObject) -> None:
    try:
        docstring = obj.docstring
        if not docstring or not docstring.value:
            return

        logger.debug(f"Processing docstring for {obj.path}")
        logger.debug(f"Docstring content: {docstring.value}")

        usage_docs_match = safe_regex_search(
            r"usage[\s-]*docs:[\s]*(\S+)", docstring.value, flags=re.I
        )
        if not usage_docs_match:
            logger.debug(f"No usage docs link found in docstring for {obj.path}")
            return

        usage_docs_link = usage_docs_match.group(1)
        logger.debug(f"Found usage docs link: {usage_docs_link}")

        # Parse the usage docs link
        parsed_link = urlparse(usage_docs_link)

        if parsed_link.netloc == "mirascope.com":
            local_link = parsed_link.path.lstrip("/")
        else:
            local_link = usage_docs_link

        # Split the local link into path and fragment
        local_path, _, fragment = local_link.partition("#")

        usage_file_path = DOCS_PATH / local_path.rstrip("/")
        if not usage_file_path.exists():
            usage_file_path = usage_file_path.with_suffix(".md")

        if not usage_file_path.exists():
            logger.warning(f"Usage docs file not found: {usage_file_path}")
            return

        local_api_link = get_local_api_link(obj.path)
        insert_or_update_api_section(usage_file_path, local_api_link, obj.path)

        # Reconstruct the link with the fragment
        full_local_link = f"/{local_path}"
        if fragment:
            full_local_link += f"#{fragment}"

        # Create the usage docs section
        usage_docs_section = f'??? abstract "Usage Documentation"\n    [{usage_file_path.stem.replace("_", " ").title()}]({full_local_link})\n\n'

        # Replace the original usage docs line with the new section
        docstring.value = re.sub(
            r"usage[\s-]*docs:[\s]*\S+\n?",
            usage_docs_section,
            docstring.value,
            flags=re.I,
        )

        logger.debug(f"Successfully updated links for {obj.path}")
    except Exception as e:
        logger.error(f"Error in update_links for {obj.path}: {str(e)}")
        logger.debug(traceback.format_exc())


class UpdateDocstringsExtension(Extension):
    def on_instance(  # type: ignore
        self, *, node: ast.AST | ObjectNode, obj: GriffeObject, agent: Any
    ) -> None:
        try:
            if not obj.is_alias and obj.docstring is not None:
                update_links(obj)
        except Exception as e:
            logger.error(f"Error in UpdateDocstringsExtension for {obj.path}: {str(e)}")
            logger.debug(traceback.format_exc())


# Add a hook to catch and log any unhandled exceptions
def exception_handler(exctype: Any, value: Any, tb: Any) -> None:
    logger.error("Unhandled exception:", exc_info=(exctype, value, tb))


sys.excepthook = exception_handler
