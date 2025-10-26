import io
import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal, Self

from ....content import (
    AssistantContentPart,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
    Thought,
    ThoughtChunk,
    ThoughtEndChunk,
    ThoughtStartChunk,
    ToolCall,
    ToolCallChunk,
    ToolCallEndChunk,
    ToolCallStartChunk,
)
from ....responses import ChunkIterator


@dataclass(frozen=True)
class WrapperTokens:
    """Represents a pair of start and end tokens used to wrap special sections in text."""

    start: str
    """The token that indicates the start of a special section."""

    end: str
    """The token that indicates the end of a special section."""

    @classmethod
    def xml_like(cls, tag: str) -> Self:
        """Creates XML-like wrapper tokens with the specified tag. For example, for qwen
        style <think> and </think> tags."""

        return cls(f"<{tag}>", f"</{tag}>")


@dataclass(frozen=True)
class SpecialTokens:
    thinking_wrappers: WrapperTokens | None = None
    tool_call_wrappers: WrapperTokens | None = None

    @classmethod
    def qwen3(cls) -> Self:
        return cls(
            thinking_wrappers=WrapperTokens.xml_like("think"),
            tool_call_wrappers=WrapperTokens.xml_like("tool_call"),
        )

    @classmethod
    def flat_text(cls) -> Self:
        return cls()

    def is_thinking_start(self, token: str) -> bool:
        if self.thinking_wrappers is None:
            return False

        return token == self.thinking_wrappers.start

    def is_thinking_end(self, token: str) -> bool:
        if self.thinking_wrappers is None:
            return False

        return token == self.thinking_wrappers.end

    def is_tool_call_start(self, token: str) -> bool:
        if self.tool_call_wrappers is None:
            return False

        return token == self.tool_call_wrappers.start

    def is_tool_call_end(self, token: str) -> bool:
        if self.tool_call_wrappers is None:
            return False

        return token == self.tool_call_wrappers.end


class TextProcessor:
    """Processes a stream of text into structured chunks based on special tokens."""

    def __init__(self, special_tokens: SpecialTokens, min_length: int) -> None:
        self._special_tokens = special_tokens
        self._min_length = min_length
        self._state: Literal["text", "tool_call", "thought"] | None = None
        self._buffer = io.StringIO()

    @classmethod
    def process_text_stream(
        cls, text_stream: Iterable[str], special_tokens: SpecialTokens, min_length: int
    ) -> ChunkIterator:
        processor = cls(special_tokens=special_tokens, min_length=min_length)
        for text in text_stream:
            yield from processor.process_text(text)
        yield from processor.flush()

    @classmethod
    def process_text_stream_to_contents(
        cls,
        text_stream: Iterable[str],
        special_tokens: SpecialTokens,
    ) -> Iterable[AssistantContentPart]:
        last_tool_call_start: ToolCallStartChunk | None = None

        for chunk in cls.process_text_stream(
            text_stream=text_stream,
            special_tokens=special_tokens,
            min_length=-1,
        ):
            if chunk.type == "text_chunk":
                yield Text(text=chunk.delta)
            elif chunk.type == "text_start_chunk" or chunk.type == "text_end_chunk":
                pass
            elif chunk.type == "thought_chunk":
                yield Thought(thought=chunk.delta)
            elif (
                chunk.type == "thought_start_chunk" or chunk.type == "thought_end_chunk"
            ):
                pass
            elif chunk.type == "tool_call_start_chunk":
                last_tool_call_start = chunk
            elif chunk.type == "tool_call_chunk":
                yield ToolCall(
                    id=last_tool_call_start.id if last_tool_call_start else "",
                    name=last_tool_call_start.name if last_tool_call_start else "",
                    args=chunk.delta,
                )
            elif chunk.type == "tool_call_end_chunk":
                pass
            else:
                raise NotImplementedError(f"Unsupported chunk type: {chunk}")

    def reset(self) -> str:
        """Resets the internal buffer and returns its content."""

        result = self._buffer.getvalue()
        self._buffer = io.StringIO()
        return result

    def flush_contents(self) -> ChunkIterator:
        """Flushes any buffered content and yields corresponding content chunks."""

        text = self.reset()
        if len(text) == 0:
            return
        if self._state == "text":
            yield TextChunk(delta=text)
        elif self._state == "thought":
            yield ThoughtChunk(delta=text)
        elif self._state == "tool_call":
            try:
                text_json = json.loads(text)
                name = text_json.get("name", "")
                args = json.dumps(text_json.get("arguments", {}))
            except json.JSONDecodeError:
                name = ""
                args = ""

            yield ToolCallStartChunk(id="", name=name)
            yield ToolCallChunk(delta=args)
            yield ToolCallEndChunk()
            self._state = None

    def flush(self) -> ChunkIterator:
        """Flushes any buffered content and yields necessary end chunks."""

        yield from self.flush_contents()

        assert self._state != "tool_call", (
            "Tool call end must be handled in flush_contents"
        )
        if self._state == "text":
            yield TextEndChunk()
        elif self._state == "thought":
            yield ThoughtEndChunk()

        self._state = None

    def _start_text(self) -> ChunkIterator:
        yield TextStartChunk()
        self._state = "text"

    def _start_thought(self) -> ChunkIterator:
        yield ThoughtStartChunk()
        self._state = "thought"

    def process_text(self, text: str) -> ChunkIterator:
        """Processes a single text token and yields structured chunks as needed."""

        if self._special_tokens.is_thinking_start(text):
            yield from self.flush()
            yield from self._start_thought()
            self._state = "thought"
        elif self._special_tokens.is_thinking_end(text):
            yield from self.flush()
        elif self._special_tokens.is_tool_call_start(text):
            yield from self.flush()
            self._state = "tool_call"
            # Tool call emission always happens at the end because
            # we need to parse the full JSON to get the tool name.
        elif self._special_tokens.is_tool_call_end(text):
            yield from self.flush()
        else:
            if self._state is None:
                yield from self._start_text()

            self._buffer.write(text)
            # We postpone emitting tool_call content to the end, because the full
            # json is required to correctly emit the tool call chunks.
            if (
                self._state != "tool_call"
                and self._min_length >= 0
                and len(self._buffer.getvalue()) > self._min_length
            ):
                if self._state == "text":
                    yield TextChunk(delta=self.reset())
                elif self._state == "thought":
                    yield ThoughtChunk(delta=self.reset())
