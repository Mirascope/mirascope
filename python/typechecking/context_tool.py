"""Type safety testing for tools and context tools"""

from mirascope import llm


def no_context() -> int:
    return 42


def async_no_context() -> int:
    return 42


def deps_mismatch_failures():
    llm.context_tool(no_context)  # type: ignore[reportCallIssue]
    llm.context_tool(async_no_context)  # type: ignore[reportCallIssue]
