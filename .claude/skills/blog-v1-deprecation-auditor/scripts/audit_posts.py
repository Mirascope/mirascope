#!/usr/bin/env python3
"""
Blog Post Auditor Script

Scans all MDX blog posts and generates a report of outdated elements.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class Issue:
    """Represents a single issue found in a blog post."""

    category: str
    priority: str  # HIGH, MEDIUM, LOW
    line_number: int
    description: str
    found_text: str


@dataclass
class PostAudit:
    """Audit results for a single blog post."""

    filename: str
    title: str = ""
    date: str = ""
    completed: str | None = None  # Date string if v2_migration_completed
    issues: list[Issue] = field(default_factory=list)

    @property
    def priority_score(self) -> int:
        """Calculate priority score for sorting."""
        scores = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        return sum(scores.get(i.priority, 0) for i in self.issues)

    @property
    def highest_priority(self) -> str:
        """Get the highest priority level among issues."""
        if not self.issues:
            return "NONE"
        priorities = ["HIGH", "MEDIUM", "LOW"]
        for p in priorities:
            if any(i.priority == p for i in self.issues):
                return p
        return "LOW"


# Patterns to detect
PATTERNS = {
    # HIGH priority - Lilypad (Deprecated branding - now Mirascope Cloud)
    "lilypad_import": {
        "pattern": r"import lilypad",
        "category": "Lilypad (Deprecated)",
        "priority": "HIGH",
        "description": "Lilypad import - Lilypad is now Mirascope Cloud",
    },
    "lilypad_configure": {
        "pattern": r"lilypad\.configure\(",
        "category": "Lilypad (Deprecated)",
        "priority": "HIGH",
        "description": "Lilypad configure call - now ops.configure()",
    },
    "lilypad_trace": {
        "pattern": r"@lilypad\.trace\(",
        "category": "Lilypad (Deprecated)",
        "priority": "HIGH",
        "description": "Lilypad trace decorator - now @ops.trace or @ops.version",
    },
    "lilypad_docs_link": {
        "pattern": r"\(/docs/lilypad",
        "category": "Lilypad (Deprecated)",
        "priority": "HIGH",
        "description": "Link to Lilypad docs (no longer available, now /docs/learn/ops)",
    },
    "lilypad_screenshot": {
        "pattern": r"!\[.*\]\(/assets/blog/[^)]*lilypad[^)]*\)",
        "category": "Lilypad (Deprecated)",
        "priority": "HIGH",
        "description": "Lilypad UI screenshot (outdated - UI has changed)",
    },
    "lilypad_description": {
        "pattern": r"Lilypad is",
        "category": "Lilypad (Deprecated)",
        "priority": "HIGH",
        "description": "Lilypad product description (branding changed to Mirascope Cloud)",
    },
    "lilypad_feature_prose": {
        "pattern": r"Lilypad (traces|versions|provides|enables|allows|offers|helps|lets|'s)",
        "category": "Lilypad (Deprecated)",
        "priority": "HIGH",
        "description": "Prose describing Lilypad features",
    },
    # HIGH priority - Prose references to deprecated APIs (inline code in prose)
    "prose_openai_call": {
        "pattern": r"`@openai\.call`",
        "category": "Prose (Deprecated API)",
        "priority": "HIGH",
        "description": "Prose references @openai.call decorator",
    },
    "prose_anthropic_call": {
        "pattern": r"`@anthropic\.call`",
        "category": "Prose (Deprecated API)",
        "priority": "HIGH",
        "description": "Prose references @anthropic.call decorator",
    },
    "prose_provider_call": {
        "pattern": r"`@(gemini|mistral|groq|cohere|litellm|azure|vertex|bedrock)\.call`",
        "category": "Prose (Deprecated API)",
        "priority": "HIGH",
        "description": "Prose references provider-specific decorator",
    },
    "prose_mirascope_core": {
        "pattern": r"`mirascope\.core`",
        "category": "Prose (Deprecated API)",
        "priority": "HIGH",
        "description": "Prose references mirascope.core module",
    },
    "prose_lilypad_decorator": {
        "pattern": r"`@?lilypad\.(trace|configure)`",
        "category": "Prose (Deprecated API)",
        "priority": "HIGH",
        "description": "Prose references Lilypad API",
    },
    # MEDIUM priority - Provider-specific explanations in prose
    "provider_specific_prose": {
        "pattern": r"provider[- ]specific (decorator|call|import|API)",
        "category": "Prose (API Design)",
        "priority": "MEDIUM",
        "description": "Prose explaining provider-specific pattern",
    },
    # HIGH priority - Legacy API syntax (v1)
    "old_import_provider": {
        "pattern": r"from mirascope\.core import (openai|anthropic|gemini|mistral|groq|cohere|litellm|azure|vertex|bedrock)",
        "category": "Legacy API (v1)",
        "priority": "HIGH",
        "description": "Old provider-specific import from mirascope.core",
    },
    "old_import_core": {
        "pattern": r"from mirascope\.core import",
        "category": "Legacy API (v1)",
        "priority": "HIGH",
        "description": "Import from mirascope.core (legacy v1 pattern)",
    },
    "old_import_messages": {
        "pattern": r"from mirascope\.core import.*Messages",
        "category": "Legacy API (v1)",
        "priority": "HIGH",
        "description": "Old Messages import - now llm.messages.system/user",
    },
    "old_decorator_openai": {
        "pattern": r"@openai\.call\(",
        "category": "Legacy API (v1)",
        "priority": "HIGH",
        "description": "Old OpenAI-specific decorator",
    },
    "old_decorator_anthropic": {
        "pattern": r"@anthropic\.call\(",
        "category": "Legacy API (v1)",
        "priority": "HIGH",
        "description": "Old Anthropic-specific decorator",
    },
    "old_decorator_gemini": {
        "pattern": r"@gemini\.call\(",
        "category": "Legacy API (v1)",
        "priority": "HIGH",
        "description": "Old Gemini-specific decorator",
    },
    "old_decorator_other": {
        "pattern": r"@(mistral|groq|cohere|litellm|azure|vertex|bedrock)\.call\(",
        "category": "Legacy API (v1)",
        "priority": "HIGH",
        "description": "Old provider-specific decorator",
    },
    # MEDIUM priority - Model names
    "dated_claude_model": {
        "pattern": r"claude-3-5-sonnet-\d{8}|claude-3-opus-\d{8}|claude-3-sonnet-\d{8}|claude-3-haiku-\d{8}",
        "category": "Model Name",
        "priority": "MEDIUM",
        "description": "Dated Anthropic model version",
    },
    # MEDIUM priority - Year references
    "year_in_title": {
        "pattern": r'^title:.*\b(202[0-5])\b',
        "category": "Year Reference",
        "priority": "MEDIUM",
        "description": "Outdated year in title (pre-2026)",
    },
    # HIGH priority - Invalid documentation paths
    "docs_mirascope_path": {
        "pattern": r"\(/docs/mirascope[/)]",
        "category": "Documentation Link",
        "priority": "HIGH",
        "description": "Invalid /docs/mirascope path - v2 uses /docs/ directly",
    },
    "old_docs_v1": {
        "pattern": r"\(/docs/v1/",
        "category": "Documentation Link",
        "priority": "HIGH",
        "description": "Legacy v1 docs link - NEVER link to /docs/v1/",
    },
    # MEDIUM priority - Documentation links
    "docs_specific_guide": {
        "pattern": r"\(/docs/guides/[^)]+\)",
        "category": "Documentation Link",
        "priority": "MEDIUM",
        "description": "Specific guide link - guides not ready, use /docs/guides index only",
    },
    # LOW priority - Various checks
    "image_reference": {
        "pattern": r"!\[.*\]\(/assets/blog/",
        "category": "Image Reference",
        "priority": "HIGH",
        "description": "Blog image (review if UI screenshot)",
    },
    # HIGH priority - Response API (v1)
    "old_response_model_dump": {
        "pattern": r"\.model_dump\(\)",
        "category": "Response API (v1)",
        "priority": "HIGH",
        "description": "Possible v1 response.model_dump() - v2 uses response.raw.model_dump_json(indent=2)",
    },
    "prose_response_model_dump": {
        "pattern": r"`[a-z_]+\.model_dump\(\)`",
        "category": "Prose (Deprecated API)",
        "priority": "HIGH",
        "description": "Prose references old model_dump() pattern",
    },
}


def extract_frontmatter(content: str) -> dict[str, str]:
    """Extract frontmatter fields from MDX content."""
    frontmatter: dict[str, str] = {}
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if match:
        fm_content = match.group(1)
        for line in fm_content.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip().strip('"')
    return frontmatter


def find_code_block_context(
    lines: list[str], flagged_line_nums: set[int], context_lines: int = 3
) -> list[Issue]:
    """Find prose context around flagged code blocks.

    When a code block contains deprecated patterns, the prose before and after
    the code block often contains explanations that also need updating.
    """
    context_issues = []
    in_code_block = False
    code_block_start = 0

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            if not in_code_block:
                # Starting a code block
                in_code_block = True
                code_block_start = i
            else:
                # Ending a code block - check if any lines inside were flagged
                code_block_end = i
                block_has_issues = any(
                    code_block_start <= ln <= code_block_end for ln in flagged_line_nums
                )

                if block_has_issues:
                    # Flag context before code block
                    for ctx_line in range(
                        max(1, code_block_start - context_lines), code_block_start
                    ):
                        line_content = lines[ctx_line - 1].strip()
                        # Only flag non-empty lines that aren't already flagged
                        if ctx_line not in flagged_line_nums and line_content:
                            context_issues.append(
                                Issue(
                                    category="Prose Context",
                                    priority="MEDIUM",
                                    line_number=ctx_line,
                                    description="Prose before flagged code block (review for accuracy)",
                                    found_text=line_content[:80],
                                )
                            )

                    # Flag context after code block
                    for ctx_line in range(
                        code_block_end + 1,
                        min(len(lines) + 1, code_block_end + context_lines + 1),
                    ):
                        line_content = lines[ctx_line - 1].strip()
                        # Only flag non-empty lines that aren't already flagged
                        # and aren't the start of another code block
                        if (
                            ctx_line not in flagged_line_nums
                            and line_content
                            and not line_content.startswith("```")
                        ):
                            context_issues.append(
                                Issue(
                                    category="Prose Context",
                                    priority="MEDIUM",
                                    line_number=ctx_line,
                                    description="Prose after flagged code block (review for accuracy)",
                                    found_text=line_content[:80],
                                )
                            )

                in_code_block = False
                code_block_start = 0

    return context_issues


def audit_post(filepath: Path) -> PostAudit:
    """Audit a single blog post for issues."""
    content = filepath.read_text()
    lines = content.split("\n")
    filename = filepath.name

    # Extract frontmatter
    frontmatter = extract_frontmatter(content)
    audit = PostAudit(
        filename=filename,
        title=frontmatter.get("title", ""),
        date=frontmatter.get("date", ""),
        completed=frontmatter.get("v2_migration_completed"),
    )

    # Check each pattern against each line
    for line_num, line in enumerate(lines, 1):
        for pattern_name, pattern_info in PATTERNS.items():
            match = re.search(pattern_info["pattern"], line)
            if match:
                audit.issues.append(
                    Issue(
                        category=pattern_info["category"],
                        priority=pattern_info["priority"],
                        line_number=line_num,
                        description=pattern_info["description"],
                        found_text=match.group(0)[:80],  # Truncate long matches
                    )
                )

    # Collect line numbers of flagged issues for context detection
    flagged_lines = {issue.line_number for issue in audit.issues}

    # Find prose context around flagged code blocks
    context_issues = find_code_block_context(lines, flagged_lines)
    audit.issues.extend(context_issues)

    return audit


def generate_report(audits: list[PostAudit]) -> str:
    """Generate a markdown report from audit results."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Calculate statistics
    total_posts = len(audits)
    completed_posts = [a for a in audits if a.completed]
    # Filter out completed posts for the "needs work" list
    posts_with_issues = [a for a in audits if a.issues and not a.completed]
    high_priority = sum(1 for a in posts_with_issues if a.highest_priority == "HIGH")
    medium_priority = sum(1 for a in posts_with_issues if a.highest_priority == "MEDIUM")
    low_priority = sum(1 for a in posts_with_issues if a.highest_priority == "LOW")

    # Sort by date (oldest first) - YYYY-MM-DD sorts correctly as string
    posts_with_issues.sort(key=lambda a: a.date)

    report = f"""# Blog Post Audit Report

Generated: {now}

## Summary

- **Total posts**: {total_posts}
- **Posts needing updates**: {len(posts_with_issues)}
- **Posts completed**: {len(completed_posts)}
- **High priority**: {high_priority}
- **Medium priority**: {medium_priority}
- **Low priority**: {low_priority}

## Issue Categories

| Category | Count |
|----------|-------|
"""

    # Count issues by category
    category_counts: dict[str, int] = {}
    for audit in audits:
        for issue in audit.issues:
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1

    for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        report += f"| {category} | {count} |\n"

    report += "\n## Posts Requiring Updates\n\n"

    if not posts_with_issues:
        report += "*No issues found!*\n"
    else:
        for audit in posts_with_issues:
            report += f"### {audit.filename}\n\n"
            report += f"**Title**: {audit.title}\n"
            report += f"**Date**: {audit.date}\n"
            report += f"**Priority**: {audit.highest_priority}\n\n"
            report += "**Issues Found:**\n\n"

            # Group issues by category
            issues_by_category: dict[str, list[Issue]] = {}
            for issue in audit.issues:
                if issue.category not in issues_by_category:
                    issues_by_category[issue.category] = []
                issues_by_category[issue.category].append(issue)

            for category, issues in issues_by_category.items():
                report += f"#### {category}\n\n"
                for issue in issues:
                    report += f"- **Line {issue.line_number}** [{issue.priority}]: {issue.description}\n"
                    report += f"  - Found: `{issue.found_text}`\n"
                report += "\n"

            report += "---\n\n"

    # List posts with no issues (excluding completed ones)
    clean_posts = [a for a in audits if not a.issues and not a.completed]
    if clean_posts:
        report += "## Posts with No Issues\n\n"
        for audit in sorted(clean_posts, key=lambda a: a.filename):
            report += f"- {audit.filename}\n"
        report += "\n"

    # List completed posts
    if completed_posts:
        report += "## Completed Posts\n\n"
        for audit in sorted(completed_posts, key=lambda a: a.date):
            report += f"- [{audit.date}] {audit.filename} (completed: {audit.completed})\n"

    return report


def generate_summary(audits: list[PostAudit]) -> str:
    """Generate a compact summary (no detailed issues)."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Calculate statistics
    total_posts = len(audits)
    completed_posts = [a for a in audits if a.completed]
    posts_with_issues = [a for a in audits if a.issues and not a.completed]

    # Count by priority
    high_count = sum(
        sum(1 for i in a.issues if i.priority == "HIGH") for a in posts_with_issues
    )
    medium_count = sum(
        sum(1 for i in a.issues if i.priority == "MEDIUM") for a in posts_with_issues
    )
    low_count = sum(
        sum(1 for i in a.issues if i.priority == "LOW") for a in posts_with_issues
    )

    # Sort by date (oldest first)
    posts_with_issues.sort(key=lambda a: a.date)

    summary = f"""# Blog Post Audit Summary

Generated: {now}

## Stats

- **Total posts**: {total_posts}
- **Posts needing updates**: {len(posts_with_issues)}
- **Posts completed**: {len(completed_posts)}
- **Total issues**: HIGH={high_count}, MEDIUM={medium_count}, LOW={low_count}

## Top 5 Posts to Update (oldest first)

"""
    if not posts_with_issues:
        summary += "*No issues found!*\n"
    else:
        # Show top 5 prominently
        for i, audit in enumerate(posts_with_issues[:5], 1):
            high = sum(1 for issue in audit.issues if issue.priority == "HIGH")
            med = sum(1 for issue in audit.issues if issue.priority == "MEDIUM")
            low = sum(1 for issue in audit.issues if issue.priority == "LOW")
            summary += f"{i}. [{audit.date}] **{audit.filename}** (H:{high} M:{med} L:{low})\n"

        # Show remaining posts in a collapsed section
        remaining = posts_with_issues[5:]
        if remaining:
            summary += f"\n## Remaining Posts ({len(remaining)} more)\n\n"
            for i, audit in enumerate(remaining, 6):
                high = sum(1 for issue in audit.issues if issue.priority == "HIGH")
                med = sum(1 for issue in audit.issues if issue.priority == "MEDIUM")
                low = sum(1 for issue in audit.issues if issue.priority == "LOW")
                summary += f"{i}. [{audit.date}] {audit.filename} (H:{high} M:{med} L:{low})\n"

    if completed_posts:
        summary += f"\n## Completed Posts ({len(completed_posts)})\n\n"
        for audit in sorted(completed_posts, key=lambda a: a.completed or ""):
            summary += f"- {audit.filename} (completed: {audit.completed})\n"

    return summary


def generate_file_report(audit: PostAudit) -> str:
    """Generate detailed report for a single file."""
    report = f"""# Audit: {audit.filename}

**Title**: {audit.title}
**Date**: {audit.date}
**Status**: {"COMPLETED (" + audit.completed + ")" if audit.completed else "Needs review"}
**Issues**: {len(audit.issues)}

"""
    if not audit.issues:
        report += "*No issues found in this file.*\n"
        return report

    # Group issues by category
    issues_by_category: dict[str, list[Issue]] = {}
    for issue in audit.issues:
        if issue.category not in issues_by_category:
            issues_by_category[issue.category] = []
        issues_by_category[issue.category].append(issue)

    for category, issues in issues_by_category.items():
        report += f"## {category}\n\n"
        for issue in sorted(issues, key=lambda i: i.line_number):
            report += f"- **Line {issue.line_number}** [{issue.priority}]: {issue.description}\n"
            report += f"  - Found: `{issue.found_text}`\n"
        report += "\n"

    return report


def find_blog_dir() -> Path | None:
    """Find the blog directory."""
    blog_dir = Path("content/blog")
    if blog_dir.exists():
        return blog_dir
    # Try from repo root
    blog_dir = Path(__file__).parent.parent.parent.parent.parent / "content" / "blog"
    if blog_dir.exists():
        return blog_dir
    return None


def main():
    """Main entry point.

    Usage:
        audit_posts.py              # Summary only (default)
        audit_posts.py --file X.mdx # Detailed audit for one file
    """
    import sys

    blog_dir = find_blog_dir()
    if not blog_dir:
        print("Error: Could not find blog directory")
        return

    # Parse arguments
    args = sys.argv[1:]
    single_file = None

    if "--file" in args:
        idx = args.index("--file")
        if idx + 1 < len(args):
            single_file = args[idx + 1]
        else:
            print("Error: --file requires a filename")
            return

    posts = sorted(blog_dir.glob("*.mdx"))

    if single_file:
        # Single file mode - detailed audit
        target = blog_dir / single_file
        if not target.exists():
            # Try matching without full path
            matches = [p for p in posts if p.name == single_file]
            if matches:
                target = matches[0]
            else:
                print(f"Error: File not found: {single_file}")
                print(f"Available files: {[p.name for p in posts[:5]]}...")
                return

        audit = audit_post(target)
        print(generate_file_report(audit))
    else:
        # Summary mode - scan all, show compact summary
        print(f"Scanning {len(posts)} blog posts...")
        audits = []
        for post in posts:
            audit = audit_post(post)
            audits.append(audit)

        print(generate_summary(audits))


if __name__ == "__main__":
    main()
