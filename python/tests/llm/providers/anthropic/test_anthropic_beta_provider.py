"""Tests for llm.providers.AnthropicProvider with beta features."""

import json
import re
from enum import Enum
from typing import Annotated, Any, Literal, NoReturn, cast
from unittest.mock import MagicMock, patch

import pytest
from anthropic import RateLimitError as AnthropicRateLimitError
from anthropic.types.beta import BetaMessageDeltaUsage, BetaRawMessageDeltaEvent
from anthropic.types.beta.beta_raw_message_delta_event import Delta
from pydantic import BaseModel, Field

from mirascope import llm
from mirascope.llm.providers.anthropic._utils import beta_decode, beta_encode
from mirascope.llm.providers.anthropic.beta_provider import AnthropicBetaProvider


@pytest.mark.parametrize("strict", [None, True, False])
def test_annotated_constraints_in_strict_tools(strict: bool | None) -> None:
    """Strict requests use Anthropic's supported schema without losing local constraints."""

    class Details(BaseModel):
        code: Annotated[str, Field(min_length=2, max_length=5)]

    @llm.tool(strict=strict)
    def constrained_tool(
        count: Annotated[int, Field(ge=1, le=5)], details: Details
    ) -> int:
        return count

    original = constrained_tool.parameters.model_dump(by_alias=True, exclude_none=True)
    _, _, kwargs = beta_encode.beta_encode_request(
        model_id="anthropic-beta/claude-sonnet-4-5",
        messages=[llm.messages.user("Use the tool")],
        tools=llm.tools.Toolkit([constrained_tool]),
        format=None,
        params={},
    )
    tools = kwargs.get("tools")
    assert isinstance(tools, list)
    encoded = cast(dict[str, Any], tools[0])
    schema = encoded["input_schema"]
    count = schema["properties"]["count"]
    code = schema["$defs"]["Details"]["properties"]["code"]
    if strict is False:
        assert count["minimum"] == 1 and count["maximum"] == 5
        assert code["minLength"] == 2 and code["maxLength"] == 5
    else:
        assert "minimum" not in count and "maximum" not in count
        assert "minimum" in count["description"] and "maximum" in count["description"]
        assert "minLength" not in code and "maxLength" not in code
        assert "minLength" in code["description"] and "maxLength" in code["description"]
    assert (
        constrained_tool.parameters.model_dump(by_alias=True, exclude_none=True)
        == original
    )


def test_strict_tool_keeps_enum_and_const() -> None:
    class Color(str, Enum):
        RED = "red"
        BLUE = "blue"

    @llm.tool
    def choices(
        mode: Literal["fast", "slow"], exact: Literal["x"], color: Color
    ) -> str:
        return mode

    _, _, kwargs = beta_encode.beta_encode_request(
        model_id="anthropic-beta/claude-sonnet-4-5",
        messages=[llm.messages.user("Use the tool")],
        tools=llm.tools.Toolkit([choices]),
        format=None,
        params={},
    )
    tools = kwargs.get("tools")
    assert isinstance(tools, list)
    schema = cast(dict[str, Any], tools[0])["input_schema"]
    assert schema["properties"]["mode"]["enum"] == ["fast", "slow"]
    assert schema["properties"]["exact"]["const"] == "x"
    assert schema["$defs"]["Color"]["enum"] == ["red", "blue"]


@pytest.mark.parametrize("annotated", [True, False])
def test_strict_tool_keeps_unconstrained_parameters(annotated: bool) -> None:
    def unconstrained(value: Any) -> str:  # noqa: ANN401 - exercise Any tool parameters
        return str(value)

    if not annotated:
        unconstrained.__annotations__ = {}
    tool = llm.tool(unconstrained)
    _, _, kwargs = beta_encode.beta_encode_request(
        model_id="anthropic-beta/claude-sonnet-4-5",
        messages=[llm.messages.user("Use the tool")],
        tools=llm.tools.Toolkit([tool]),
        format=None,
        params={},
    )
    tools = kwargs.get("tools")
    assert isinstance(tools, list)
    schema = cast(dict[str, Any], tools[0])["input_schema"]
    assert schema["properties"]["value"] == {"title": "Value"}


@pytest.mark.parametrize("minimum", [0, 1, 2])
def test_strict_tool_adapts_nested_array_constraints(minimum: int) -> None:
    @llm.tool
    def entries(
        values: Annotated[
            list[Annotated[int, Field(gt=0, multiple_of=2)]],
            Field(min_length=minimum, max_length=5),
        ],
    ) -> int:
        return len(values)

    _, _, kwargs = beta_encode.beta_encode_request(
        model_id="anthropic-beta/claude-sonnet-4-5",
        messages=[llm.messages.user("Use the tool")],
        tools=llm.tools.Toolkit([entries]),
        format=None,
        params={},
    )
    tools = kwargs.get("tools")
    assert isinstance(tools, list)
    schema = cast(dict[str, Any], tools[0])["input_schema"]["properties"]["values"]
    assert "maxItems" not in schema and "maxItems" in schema["description"]
    if minimum <= 1:
        assert schema["minItems"] == minimum
    else:
        assert "minItems" not in schema and "minItems" in schema["description"]
    assert "exclusiveMinimum" not in schema["items"]
    assert "multipleOf" not in schema["items"]
    assert "exclusiveMinimum" in schema["items"]["description"]
    assert "multipleOf" in schema["items"]["description"]


def test_strict_tool_adapts_optional_constraints() -> None:
    @llm.tool
    def optional(values: list[Annotated[int, Field(gt=0)]] | None = None) -> int:
        return len(values or [])

    _, _, kwargs = beta_encode.beta_encode_request(
        model_id="anthropic-beta/claude-sonnet-4-5",
        messages=[llm.messages.user("Use the tool")],
        tools=llm.tools.Toolkit([optional]),
        format=None,
        params={},
    )
    tools = kwargs.get("tools")
    assert isinstance(tools, list)
    schema = cast(dict[str, Any], tools[0])["input_schema"]["properties"]["values"]
    assert schema["default"] is None
    assert schema["anyOf"][1] == {"type": "null"}
    items = schema["anyOf"][0]["items"]
    assert "exclusiveMinimum" not in items
    assert "exclusiveMinimum: 0" in items["description"]
    output = optional.execute(
        llm.ToolCall(id="invalid", name=optional.name, args='{"values": [0]}')
    )
    assert isinstance(output.error, llm.ToolExecutionError)


@pytest.mark.parametrize("strict", [None, True, False])
@pytest.mark.parametrize(
    ("pattern", "valid", "invalid"),
    [
        (r"\bword\b", "a word!", "sword"),
        (r"word\B", "words", "word"),
        (r"\\\bword", "\\word", "\\sword"),
        (re.compile(r"word(?=!)"), "word!", "word?"),
        (re.compile(r"word(?!s)"), "word!", "words"),
        (re.compile(r"(?<=!)word"), "!word", "?word"),
        (re.compile(r"(?<!!)word"), "?word", "!word"),
        (re.compile(r"(word)\1"), "wordword", "word"),
        (re.compile(r"(?P<term>word)(?P=term)"), "wordword", "word"),
        (r"^[a-z]+$", "word", "123"),
        (r"^a{1,10000}$", "a", "b"),
        (r"\\bword\\b", "\\bword\\b", "word"),
        (r"[\\b]+", "bbb", "word"),
        (r"[(?=)]+", "(?=)", "word"),
        (re.compile(r"[\b]+"), "\b", "word"),
        (re.compile(r"[]\b]+"), "]", "word"),
        (re.compile(r"[^]\b]+"), "word", "]"),
        (r"\(\?=word\)", "(?=word)", "word"),
        (r"[^^]\bword", "a word", "^word"),
        (re.compile(r"[^^](?=x)"), "ax", "^x"),
        (re.compile(r"[^^](a)\1"), "xaa", "^aa"),
        (r"[^^]+", "word", "^^"),
    ],
)
def test_strict_tool_describes_patterns(
    strict: bool | None,
    pattern: str | re.Pattern[str],
    valid: str,
    invalid: str,
) -> None:
    class Details(BaseModel):
        value: Annotated[str, Field(pattern=pattern, description="A matching value.")]

    @llm.tool(strict=strict)
    def matching(
        value: Annotated[str, Field(pattern=pattern, description="A matching value.")],
        details: Details,
    ) -> str:
        return value

    original = matching.parameters.model_dump(by_alias=True, exclude_none=True)
    _, _, kwargs = beta_encode.beta_encode_request(
        model_id="anthropic-beta/claude-sonnet-4-5",
        messages=[llm.messages.user("Use the tool")],
        tools=llm.tools.Toolkit([matching]),
        format=None,
        params={},
    )
    tools = kwargs.get("tools")
    assert isinstance(tools, list)
    schema = cast(dict[str, Any], tools[0])["input_schema"]
    expected_pattern = pattern if isinstance(pattern, str) else pattern.pattern
    for field in (
        schema["properties"]["value"],
        schema["$defs"]["Details"]["properties"]["value"],
    ):
        if strict is False:
            assert field["pattern"] == expected_pattern
            assert field["description"] == "A matching value."
        else:
            assert "pattern" not in field
            assert field["description"] == (
                f"A matching value.\n\n{{pattern: {expected_pattern}}}"
            )
    assert matching.parameters.model_dump(by_alias=True, exclude_none=True) == original
    args = {"value": valid, "details": {"value": valid}}
    output = matching.execute(
        llm.ToolCall(id="valid", name=matching.name, args=json.dumps(args))
    )
    assert output.error is None
    assert output.result == valid
    for invalid_args in (
        {"value": invalid, "details": {"value": valid}},
        {"value": valid, "details": {"value": invalid}},
    ):
        output = matching.execute(
            llm.ToolCall(
                id="invalid", name=matching.name, args=json.dumps(invalid_args)
            )
        )
        assert isinstance(output.error, llm.ToolExecutionError)
        assert "String should match pattern" in str(output.error)


def test_beta_stream_rate_limit_error() -> None:
    """Test that Anthropic RateLimitError is caught and re-wrapped during beta streaming."""
    # Mock the beta stream manager to raise RateLimitError during iteration
    mock_stream_manager = MagicMock()
    mock_stream = MagicMock()
    mock_stream_manager.__enter__.return_value = mock_stream

    # Simulate rate limit error during stream iteration
    def raise_rate_limit() -> NoReturn:
        raise AnthropicRateLimitError(
            "Rate limit exceeded",
            response=MagicMock(status_code=429),
            body=None,
        )

    mock_stream._raw_stream.__iter__ = lambda self: raise_rate_limit()

    model = llm.Model("anthropic-beta/claude-sonnet-4-0")
    provider = model.provider
    assert isinstance(provider, AnthropicBetaProvider)

    # Patch the client on the already-registered provider
    with patch.object(
        provider.client.beta.messages, "stream", return_value=mock_stream_manager
    ):
        response = model.stream("test")

        # Try to finish the stream and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            response.finish()

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert "Rate limit exceeded" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, AnthropicRateLimitError)


@pytest.mark.asyncio
async def test_beta_async_stream_rate_limit_error() -> None:
    """Test that Anthropic RateLimitError is caught and re-wrapped during beta async streaming."""
    # Mock the async beta stream manager to raise RateLimitError during iteration
    mock_stream_manager = MagicMock()
    mock_stream = MagicMock()

    # Make async context manager methods actually async
    async def mock_aenter(self: object) -> MagicMock:
        return mock_stream

    async def mock_aexit(self: object, *args: object) -> None:
        return None

    mock_stream_manager.__aenter__ = mock_aenter
    mock_stream_manager.__aexit__ = mock_aexit

    # Create an async iterator that raises RateLimitError
    class MockAsyncIterator:
        def __aiter__(self) -> "MockAsyncIterator":
            return self

        async def __anext__(self) -> NoReturn:
            raise AnthropicRateLimitError(
                "Rate limit exceeded",
                response=MagicMock(status_code=429),
                body=None,
            )

    mock_stream._raw_stream = MockAsyncIterator()

    model = llm.Model("anthropic-beta/claude-sonnet-4-0")
    provider = model.provider
    assert isinstance(provider, AnthropicBetaProvider)

    # Patch the async client on the already-registered provider
    with patch.object(
        provider.async_client.beta.messages, "stream", return_value=mock_stream_manager
    ):
        response = await model.stream_async("test")

        # Try to finish the stream and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            await response.finish()

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert "Rate limit exceeded" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, AnthropicRateLimitError)


def test_beta_call_rate_limit_error() -> None:
    """Test that Anthropic RateLimitError is caught and re-wrapped during beta non-streaming calls."""
    model = llm.Model("anthropic-beta/claude-sonnet-4-0")
    provider = model.provider
    assert isinstance(provider, AnthropicBetaProvider)

    # Patch the client to raise RateLimitError
    with patch.object(
        provider.client.beta.messages,
        "parse",
        side_effect=AnthropicRateLimitError(
            "Rate limit exceeded",
            response=MagicMock(status_code=429),
            body=None,
        ),
    ):
        # Try to call and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            model.call("test")

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert "Rate limit exceeded" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, AnthropicRateLimitError)


@pytest.mark.asyncio
async def test_beta_async_call_rate_limit_error() -> None:
    """Test that Anthropic RateLimitError is caught and re-wrapped during beta async non-streaming calls."""
    model = llm.Model("anthropic-beta/claude-sonnet-4-0")
    provider = model.provider
    assert isinstance(provider, AnthropicBetaProvider)

    # Patch the async client to raise RateLimitError
    with patch.object(
        provider.async_client.beta.messages,
        "parse",
        side_effect=AnthropicRateLimitError(
            "Rate limit exceeded",
            response=MagicMock(status_code=429),
            body=None,
        ),
    ):
        # Try to call and expect RateLimitError
        with pytest.raises(llm.RateLimitError) as exc_info:
            await model.call_async("test")

        # Verify it's wrapped as mirascope RateLimitError and has proper chaining
        assert isinstance(exc_info.value, llm.RateLimitError)
        assert "Rate limit exceeded" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, AnthropicRateLimitError)


def test_beta_decode_stream_usage_includes_cache_tokens() -> None:
    """Streamed input_tokens include cache tokens, matching beta_decode_response."""
    stream_manager = MagicMock()
    stream = stream_manager.__enter__.return_value
    event = BetaRawMessageDeltaEvent(
        type="message_delta",
        delta=Delta(stop_reason="end_turn"),
        usage=BetaMessageDeltaUsage(
            input_tokens=10,
            cache_read_input_tokens=200,
            cache_creation_input_tokens=30,
            output_tokens=5,
        ),
    )

    stream._raw_stream = iter([event])
    usage_chunks = [
        chunk
        for chunk in beta_decode.beta_decode_stream(
            stream_manager, include_thoughts=False
        )
        if isinstance(chunk, llm.UsageDeltaChunk)
    ]

    assert len(usage_chunks) == 1
    assert usage_chunks[0].input_tokens == 240
    assert usage_chunks[0].cache_read_tokens == 200
    assert usage_chunks[0].cache_write_tokens == 30
