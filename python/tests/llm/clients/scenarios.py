"""Shared fixtures and scenarios for LLM client testing."""

import inspect
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import wraps
from typing import Annotated, Any, Generic, Protocol, get_args
from typing_extensions import TypedDict

from pydantic import BaseModel, Field

from mirascope import llm


class ScenarioFn(Protocol):
    """Protocol for functions that return a Scenario"""

    def __call__(self, model_id: str) -> "Scenario": ...


class CallKwargs(TypedDict, Generic[llm.tools.ToolT], total=False):
    """Shared kwargs for both sync and async client calls."""

    model_id: str
    messages: Sequence[llm.Message]
    format: type[BaseModel] | None
    tools: Sequence[llm.tools.ToolT] | None
    params: llm.clients.BaseParams | None


def _create_async_tool(
    fn: llm.tools.protocols.ToolFn[llm.types.P, llm.types.JsonableCovariantT],
) -> llm.AsyncTool[llm.types.P, llm.types.JsonableCovariantT]:
    @wraps(fn)
    async def wrapper(
        *args: llm.types.P.args, **kwargs: llm.types.P.kwargs
    ) -> llm.types.JsonableCovariantT:
        return fn(*args, **kwargs)

    return llm.tool(wrapper)


@dataclass
class Scenario(Generic[llm.types.P]):
    """A specific scenario for client testing.

    Scenario should have deterministic outputs for cross-provider consistency.
    """

    scenario_assertions: Callable[
        [llm.responses.RootResponse[Any, Any]],
        None,
    ]

    model_id: str
    messages: Sequence[llm.Message]
    format: type[BaseModel] | None = None
    tool_fns: Sequence[llm.tools.protocols.ToolFn[llm.types.P]] | None = None
    params: llm.clients.BaseParams | None = None

    @property
    def call_args(self) -> CallKwargs[llm.Tool]:
        args: CallKwargs[llm.Tool] = {
            "model_id": self.model_id,
            "messages": self.messages,
            "format": self.format,
            "params": self.params,
        }
        if self.tool_fns:
            args["tools"] = [llm.tool(tool_fn) for tool_fn in self.tool_fns]
        return args

    @property
    def call_async_args(self) -> CallKwargs[llm.AsyncTool]:
        args: CallKwargs[llm.AsyncTool] = {
            "model_id": self.model_id,
            "messages": self.messages,
            "format": self.format,
            "params": self.params,
        }
        if self.tool_fns:
            args["tools"] = [_create_async_tool(tool_fn) for tool_fn in self.tool_fns]
        return args

    def check_response(
        self,
        response: llm.responses.RootResponse[Any, Any],
    ) -> None:
        assert response.model_id == self.model_id
        self.scenario_assertions(response)


def get_scenario(scenario_id: str, model_id: str) -> Scenario:
    scenario_fn: ScenarioFn = globals()[scenario_id]
    if not scenario_fn:
        raise KeyError(f"Unknown scenario: {scenario_id}")
    scenario = scenario_fn(model_id=model_id)
    return scenario


def get_structured_scenario(
    scenario_id: str, model_id: str, formatting_mode: llm.formatting.FormattingMode
) -> Scenario:
    assert scenario_id.startswith("structured_output_")
    scenario = get_scenario(scenario_id, model_id=model_id)
    format_type = scenario.format
    assert format_type is not None
    llm.format(mode=formatting_mode)(format_type)
    return scenario


def simple_message_scenario(model_id: str) -> Scenario:
    """Simple message scenario."""

    def scenario_assertions(response: llm.responses.RootResponse) -> None:
        assert "8282" in response.pretty(), f"8282 not in response: {response.pretty()}"
        assert response.finish_reason == llm.FinishReason.END_TURN

    return Scenario(
        model_id=model_id,
        messages=[llm.messages.user("What is 8200 + 82?")],
        scenario_assertions=scenario_assertions,
    )


def multi_message_scenario(model_id: str) -> Scenario:
    """System message, conversation history, and multiple text content parts."""

    def scenario_assertions(response: llm.responses.RootResponse[Any, Any]) -> None:
        text = response.pretty()
        assert "lion" in text, f"'lion' not found in response: {text}"
        assert "walrus" in text, f"'walrus' not found in response: {text}"
        assert response.finish_reason == llm.FinishReason.END_TURN

    return Scenario(
        model_id=model_id,
        messages=[
            llm.messages.system(
                "Reply by naming every animal mentioned, all lowercase."
            ),
            llm.messages.user("Hello zebra"),
            # Include messages with multiple text parts for full coverage
            llm.messages.assistant(["zebra", "what else?"]),
            llm.messages.user(["Hello lion!", "Hello walrus!"]),
        ],
        scenario_assertions=scenario_assertions,
    )


def tool_call_scenario(model_id: str) -> Scenario:
    """The LLM should call multiple tools."""

    def bakst_coefficient(val: int) -> int:
        return 12 * val

    def scenario_assertions(response: llm.responses.RootResponse[Any, Any]) -> None:
        assert len(response.tool_calls) == 2, (
            f"Expected 2 tool call, got {len(response.tool_calls)}: {response.tool_calls}"
        )
        t1, t2 = response.tool_calls
        assert t1.name == "bakst_coefficient", f"t1 has wrong name: {t1.name}"
        assert t1.args == '{"val": 13}', f"t1 has wrong args: {t1.args}"
        assert t2.name == "bakst_coefficient", f"t2 has wrong name: {t2.name}"
        assert t2.args == '{"val": 17}', f"t2 has wrong args: {t2.args}"

        assert response.finish_reason in [
            llm.FinishReason.TOOL_USE,
            llm.FinishReason.END_TURN,
        ], f"Expected TOOL_USE or END_TURN, got {response.finish_reason}"

    return Scenario(
        model_id=model_id,
        messages=[
            llm.messages.user(
                "Using the provided tool, compute the bakst coefficients of 13 and 17"
            ),
        ],
        tool_fns=[bakst_coefficient],
        scenario_assertions=scenario_assertions,
    )


def tool_output_scenario(model_id: str) -> Scenario:
    """The LLM should use a tool output."""

    def password_retrieval_tool() -> str:
        return "mellon"

    def scenario_assertions(response: llm.responses.RootResponse) -> None:
        text = response.pretty()
        assert "mellon" in text, f"Expected 'mellon' in response: {text}"
        assert response.finish_reason == llm.FinishReason.END_TURN, (
            f"Expected END_TURN, got {response.finish_reason}"
        )

    return Scenario(
        model_id=model_id,
        messages=[
            llm.messages.system(
                "You are a password retrieval system. When you access the password, you "
                "MUST return it EXACTLY, with no added punctuation, spaces, or commentary."
            ),
            llm.messages.user("What is the password?"),
            llm.messages.assistant(
                llm.ToolCall(id="1234", name="password_retrieval_tool", args="{}")
            ),
            llm.messages.user(
                llm.ToolOutput(
                    id="1234", name="password_retrieval_tool", value="mellon"
                )
            ),
        ],
        tool_fns=[password_retrieval_tool],
        scenario_assertions=scenario_assertions,
    )


def structured_output_scenario(model_id: str) -> Scenario:
    class Book(BaseModel):
        title: str
        author: str

    expected = Book(title="The Name of the Wind", author="Patrick Rothfuss")

    def scenario_assertions(response: llm.responses.RootResponse) -> None:
        formatted = response.format()
        assert formatted == expected, f"Expected {expected}, got {formatted}"
        assert response.finish_reason == llm.FinishReason.END_TURN

    return Scenario(
        model_id=model_id,
        messages=[
            llm.messages.user(
                f"Extract the book: {expected.title} by {expected.author}"
            ),
        ],
        format=Book,
        scenario_assertions=scenario_assertions,
    )


def structured_output_formatting_instructions_scenario(model_id: str) -> Scenario:
    class Book(BaseModel):
        title: str
        author: str

        @classmethod
        def formatting_instructions(cls) -> str:
            return inspect.cleandoc("""
            Please output a book recommendation in JSON form.
            It should have the format {title: str, author: str} and the 
            title and author should both be in all caps.
            """)

    expected = Book(title="THE NAME OF THE WIND", author="PATRICK ROTHFUSS")

    def scenario_assertions(response: llm.responses.RootResponse) -> None:
        formatted = response.format()
        assert formatted == expected, f"Expected {expected}, got {formatted}"
        assert response.finish_reason == llm.FinishReason.END_TURN

    return Scenario(
        model_id=model_id,
        messages=[
            llm.messages.user(
                "Extract the book: The Name of the Wind by Patrick Rothfuss"
            ),
        ],
        format=Book,
        scenario_assertions=scenario_assertions,
    )


def structured_output_annotation_and_docstring_scenario(model_id: str) -> Scenario:
    class Output(BaseModel):
        """An output. The `first` value should be the number 17."""

        first: int
        second: Annotated[int, Field(description="Should be the number 13")]

    expected = Output(first=17, second=13)

    def scenario_assertions(response: llm.responses.RootResponse) -> None:
        formatted = response.format()
        assert formatted == expected, f"Expected {expected}, got {formatted}"
        assert response.finish_reason == llm.FinishReason.END_TURN

    return Scenario(
        model_id=model_id,
        messages=[
            llm.messages.user("Produce a formatted output"),
        ],
        format=Output,
        scenario_assertions=scenario_assertions,
    )


def structured_output_calls_tool_scenario(model_id: str) -> Scenario:
    class Book(BaseModel):
        title: str
        author: str

    def retrieve_book_tool() -> str:
        raise NotImplementedError

    def scenario_assertions(response: llm.responses.RootResponse) -> None:
        assert len(response.tool_calls) == 1, (
            f"Expected 1 tool call, got {len(response.tool_calls)}: {response.tool_calls}"
        )
        tool_call = response.tool_calls[0]
        assert tool_call.name == "retrieve_book_tool", (
            f"Expected tool name 'retrieve_book_tool', got '{tool_call.name}'"
        )
        assert tool_call.args == "{}", (
            f"Expected empty args '{{}}', got '{tool_call.args}'"
        )

    return Scenario(
        model_id=model_id,
        messages=[
            llm.messages.user("Use the retrieve book tool and format the response"),
        ],
        format=Book,
        tool_fns=[retrieve_book_tool],
        scenario_assertions=scenario_assertions,
    )


CLIENT_SCENARIO_IDS = [
    name
    for name, obj in globals().items()
    if name != "get_scenario"
    and name != "get_structured_scenario"
    and name.endswith("_scenario")
    and callable(obj)
]
STRUCTURED_SCENARIO_IDS = [
    name for name in CLIENT_SCENARIO_IDS if name.startswith("structured_output_")
]
FORMATTING_MODES = get_args(llm.formatting.FormattingMode)
