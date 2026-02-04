"""Pattern detection for Mirascope v0/v1 to v2 migration."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LegacyPattern:
    """A detected legacy (v0 or v1) pattern in the codebase."""

    file: str
    line: int
    pattern_type: str
    match: str
    description: str
    version: str  # "v0" or "v1"


# Legacy patterns to detect with their regexes and descriptions
# Organized by version for clarity
LEGACY_PATTERNS: dict[str, dict[str, str]] = {
    # ==================== V0 PATTERNS ====================
    # v0 used class-based approach with provider-specific imports
    "v0_provider_import": {
        "regex": r"from mirascope\.(?:openai|anthropic|gemini|groq|mistral|cohere|litellm) import",
        "description": "[v0] Provider-specific import (e.g., from mirascope.openai)",
        "version": "v0",
    },
    "v0_call_class": {
        "regex": r"class\s+\w+\s*\(\s*(?:OpenAI|Anthropic|Gemini|Groq|Mistral|Cohere|LiteLLM)Call\s*\)",
        "description": "[v0] Class-based call (e.g., class Foo(OpenAICall))",
        "version": "v0",
    },
    "v0_extractor_class": {
        "regex": r"class\s+\w+\s*\(\s*(?:OpenAI|Anthropic|Gemini|Groq|Mistral|Cohere|LiteLLM)Extractor",
        "description": "[v0] Class-based extractor (e.g., class Foo(OpenAIExtractor[T]))",
        "version": "v0",
    },
    "v0_tool_class": {
        "regex": r"class\s+\w+\s*\(\s*(?:OpenAI|Anthropic|Gemini|Groq|Mistral|Cohere|LiteLLM)Tool\s*\)",
        "description": "[v0] Provider-specific tool class (e.g., class Foo(OpenAITool))",
        "version": "v0",
    },
    "v0_call_params": {
        "regex": r"(?:OpenAI|Anthropic|Gemini|Groq|Mistral|Cohere|LiteLLM)CallParams",
        "description": "[v0] Provider-specific CallParams",
        "version": "v0",
    },
    "v0_prompt_template_attr": {
        "regex": r"^\s*prompt_template\s*=\s*[\"']",
        "description": "[v0] Class attribute prompt_template = '...'",
        "version": "v0",
    },
    "v0_call_async_method": {
        "regex": r"\.call_async\s*\(",
        "description": "[v0] .call_async() method (use async def + await in v2)",
        "version": "v0",
    },
    "v0_extract_method": {
        "regex": r"\.extract\s*\(",
        "description": "[v0] .extract() method (use response_model in v2)",
        "version": "v0",
    },
    "v0_response_dump": {
        "regex": r"\.dump\s*\(",
        "description": "[v0] .dump() method (use .model_dump() in v2)",
        "version": "v0",
    },
    # ==================== V1 PATTERNS ====================
    # v1 used decorator-based approach with mirascope.core imports
    "v1_provider_import": {
        "regex": r"from mirascope\.core(?:\.(\w+))? import",
        "description": "[v1] Provider-specific import (mirascope.core)",
        "version": "v1",
    },
    "v1_provider_call_decorator": {
        # Explicitly match v1 provider names, exclude 'llm' which is v2
        "regex": r"@(openai|anthropic|gemini|groq|mistral|cohere|litellm|google|azure|vertex)\.call\(\s*[\"']([^\"']+)[\"']",
        "description": "[v1] Provider-specific @provider.call() decorator",
        "version": "v1",
    },
    "v1_base_tool_import": {
        "regex": r"from mirascope\.core(?:\.\w+)? import.*BaseTool",
        "description": "[v1] BaseTool import (class-based tools)",
        "version": "v1",
    },
    "v1_base_tool_class": {
        "regex": r"class\s+\w+\s*\(\s*BaseTool\s*\)",
        "description": "[v1] Class-based tool extending BaseTool",
        "version": "v1",
    },
    "v1_prompt_template_decorator": {
        "regex": r"@prompt_template",
        "description": "[v1] @prompt_template decorator (not needed in v2)",
        "version": "v1",
    },
    "v1_stream_param_in_decorator": {
        # Match v1 provider names only, not @llm.call which is v2
        "regex": r"@(openai|anthropic|gemini|groq|mistral|cohere|litellm|google|azure|vertex)\.call\([^)]*stream\s*=\s*True",
        "description": "[v1] stream=True in decorator (use .stream() method in v2)",
        "version": "v1",
    },
    "v1_messages_kwarg": {
        "regex": r"messages\s*=\s*response\.messages",
        "description": "[v1] messages continuation pattern (use .resume() in v2)",
        "version": "v1",
    },
    "v1_response_model_param": {
        # v1 used response_model, v2 uses format
        "regex": r"@\w+\.call\([^)]*response_model\s*=",
        "description": "[v1] response_model parameter (use format= in v2)",
        "version": "v1",
    },
    "v1_llm_call_with_stream": {
        # @llm.call with stream=True is v1 pattern
        "regex": r"@llm\.call\([^)]*stream\s*=\s*True",
        "description": "[v1] stream=True in @llm.call (use .stream() method in v2)",
        "version": "v1",
    },
    # ==================== SHARED V0/V1 PATTERNS ====================
    # These patterns exist in both v0 and v1
    "response_content_access": {
        "regex": r"\.content(?!\s*\()",
        "description": "[v0/v1] Direct .content access (use .text() in v2)",
        "version": "v0/v1",
    },
    "response_tool_single": {
        # Negative lookbehind to avoid matching @llm.tool decorator
        "regex": r"(?<!@llm)\.tool(?!_calls|s\b)",
        "description": "[v0/v1] Single .tool access (use .tool_calls in v2)",
        "version": "v0/v1",
    },
}


# Backwards compatibility alias
V1Pattern = LegacyPattern


def scan_file_for_patterns(filepath: Path) -> list[LegacyPattern]:
    """Scan a single file for legacy (v0/v1) patterns.

    Args:
        filepath: Path to the Python file to scan.

    Returns:
        List of detected LegacyPattern objects.
    """
    patterns: list[LegacyPattern] = []

    try:
        content = filepath.read_text()
    except (OSError, UnicodeDecodeError):
        return patterns

    lines = content.splitlines()

    for line_num, line in enumerate(lines, start=1):
        for pattern_type, pattern_info in LEGACY_PATTERNS.items():
            if match := re.search(pattern_info["regex"], line):
                patterns.append(
                    LegacyPattern(
                        file=str(filepath),
                        line=line_num,
                        pattern_type=pattern_type,
                        match=match.group(0),
                        description=pattern_info["description"],
                        version=pattern_info["version"],
                    )
                )

    return patterns


def scan_directory_for_patterns(
    directory: Path, pattern: str = "**/*.py"
) -> dict[str, list[LegacyPattern]]:
    """Scan a directory for legacy (v0/v1) patterns.

    Args:
        directory: Directory to scan.
        pattern: Glob pattern for files to scan.

    Returns:
        Dictionary mapping file paths to lists of detected patterns.
    """
    results: dict[str, list[LegacyPattern]] = {}

    for filepath in directory.glob(pattern):
        if filepath.is_file():
            file_patterns = scan_file_for_patterns(filepath)
            if file_patterns:
                results[str(filepath)] = file_patterns

    return results


def summarize_patterns(
    patterns: dict[str, list[LegacyPattern]],
) -> dict[str, int]:
    """Summarize pattern counts by type.

    Args:
        patterns: Dictionary of file paths to pattern lists.

    Returns:
        Dictionary of pattern type to count.
    """
    summary: dict[str, int] = {}

    for file_patterns in patterns.values():
        for pattern in file_patterns:
            summary[pattern.pattern_type] = summary.get(pattern.pattern_type, 0) + 1

    return summary


def get_version_summary(
    patterns: dict[str, list[LegacyPattern]],
) -> dict[str, int]:
    """Summarize pattern counts by version (v0, v1, or v0/v1).

    Args:
        patterns: Dictionary of file paths to pattern lists.

    Returns:
        Dictionary of version to count.
    """
    summary: dict[str, int] = {}

    for file_patterns in patterns.values():
        for pattern in file_patterns:
            summary[pattern.version] = summary.get(pattern.version, 0) + 1

    return summary
