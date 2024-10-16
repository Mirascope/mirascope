try:
    from cohere import StreamEndStreamedChatResponse, StreamStartStreamedChatResponse
    from cohere.types import (
        TextGenerationStreamedChatResponse,
        ToolCallsGenerationStreamedChatResponse,
    )
except ImportError:  # pragma: no cover
    # When cohere version is less than 5.11.0
    from cohere import (
        StreamedChatResponse_StreamEnd as StreamEndStreamedChatResponse,  # pyright: ignore [reportAttributeAccessIssue]  # noqa: F401
    )
    from cohere import (
        StreamedChatResponse_StreamStart as StreamStartStreamedChatResponse,  # pyright: ignore [reportAttributeAccessIssue]  # noqa: F401
    )
    from cohere.types import (
        StreamedChatResponse_TextGeneration as TextGenerationStreamedChatResponse,  # pyright: ignore [reportAttributeAccessIssue]  # noqa: F401
    )
    from cohere.types import (
        StreamedChatResponse_ToolCallsGeneration as ToolCallsGenerationStreamedChatResponse,  # pyright: ignore [reportAttributeAccessIssue]  # noqa: F401
    )
