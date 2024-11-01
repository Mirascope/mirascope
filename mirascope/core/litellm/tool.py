"""The `LiteLLMTool` class for easy tool usage with LiteLLM LLM calls.

usage docs: learn/tools.md
"""

from ..openai import OpenAITool


class LiteLLMTool(OpenAITool):
    """A simple wrapper around `OpenAITool`.

    Since LiteLLM uses the OpenAI spec, we change nothing here.
    """
