"""The `XAITool` class for easy tool usage with xAI LLM calls.

usage docs: learn/tools.md
"""

from ..openai import OpenAITool


class XAITool(OpenAITool):
    """A simple wrapper around `OpenAITool`.

    Since xAI supports the OpenAI spec, we change nothing here.
    """
