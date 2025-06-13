"""The LLM's usage when generating a response."""

from dataclasses import dataclass


@dataclass
class Usage:
    """The usage statistics for a request to an LLM."""

    input_tokens: int
    """Number of tokens in the prompt (including messages, tools, etc)."""

    cached_tokens: int
    """Number of tokens used that were previously cached (and thus cheaper)."""

    output_tokens: int
    """Number of tokens in the generated output.
    
    TODO: figure out different types of output and how to handle that (e.g. audio)
    """

    total_tokens: int
    """Total number of tokens used in the request (prompt + completion)."""
