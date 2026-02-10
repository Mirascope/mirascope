from inline_snapshot import snapshot

from mirascope.llm import AssistantMessage, Audio, Base64AudioSource, Base64ImageSource, FinishReason, Format, Image, ProviderToolUsage, SystemMessage, Text, TextChunk, TextEndChunk, TextStartChunk, Thought, ToolCall, ToolCallChunk, ToolCallEndChunk, ToolCallStartChunk, ToolExecutionError, ToolNotFoundError, ToolOutput, URLImageSource, Usage, UserMessage

test_snapshot = snapshot()
