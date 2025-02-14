from typing_extensions import TypedDict


class StreamConfig(TypedDict):
    """Configuration options for streaming.

    Attributes:
        partial_tools (bool): Whether to stream partial tool responses
    """

    partial_tools: bool
