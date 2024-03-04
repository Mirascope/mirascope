"""Prompts with WandB and OpenAI integration to support logging functionality."""
import datetime
from typing import Literal, Union

from pydantic import BaseModel, PrivateAttr
from wandb.sdk.data_types.trace_tree import Trace

from mirascope import BaseCallParams, Prompt
from mirascope.chat.openai import OpenAIChatCompletion


class WandbPrompt(Prompt):
    '''Parent class for inherited WandB functionality.

    Use this class's built in `trace` and `trace_error` methods to log traces to WandB.

    Example:

    ```python
    import wandb
    from wandb.sdk.data_types.trace_tree import Trace
    from mirascope.wandb.integrations.wandb_prompt import WandbPrompt

    wandb.login(key="YOUR_WANDB_API_KEY")
    wandb.init(project="wandb_logged_chain")
    root_span = Trace(
        name="root",
        kind="chain",
        start_time_ms=round(datetime.datetime.now().timestamp() * 1000),
        metadata={"user": "mirascope_user"},
    )
    chat = OpenAIChat(api_key="YOUR_OPENAI_API_KEY")

    class HiPrompt(WandbPrompt):
    """{greeting}."""

    greeting: str

    prompt = HiPrompt(span_type="llm", greeting="Hello")
    completion = chat.create(prompt)
    span = prompt.trace(completion, parent=root_span)

    error_prompt = HiPrompt(span_type="llm", greeting="Hello" * 100000)
    try:
        completion = chat.create(error_prompt)
    except Exception as e:
        span = error_prompt.trace_error(e, parent=root_span)
    ```
    '''

    span_type: Literal["tool", "llm", "chain", "agent"]
    _creation_time_ms: int = PrivateAttr(
        default_factory=lambda: round(datetime.datetime.now().timestamp() * 1000)
    )

    call_params = BaseCallParams(model="gpt-3.5-turbo-0125")

    def trace(
        self, completion: Union[OpenAIChatCompletion, BaseModel], parent: Trace
    ) -> Trace:
        """Returns a trace connected to parent.

        Args:
            completion: The completion to trace. Handles `OpenAIChatCompletion` output
                from both standard OpenAI chat completions, and `BaseModel` for
                extractions.
            parent: The parent trace to connect to.

        Returns:
            The created trace, connected to the parent.
        """
        if isinstance(completion, OpenAIChatCompletion):
            if completion.tool and completion.tool.fn:
                output = {
                    "assistant": completion.tool.model_dump(),
                    "tool_output": completion.tool.fn(
                        **completion.tool.model_dump(exclude={"tool_call"})
                    ),
                }
            else:
                output = {"assistant": str(completion)}
            open_ai_chat_completion = completion
        elif isinstance(completion, BaseModel):
            output = {"assistant": str(completion.model_dump())}
            if not hasattr(completion, "_completion"):
                raise ValueError(
                    "Completion of type `BaseModel` was not created using the `extract`"
                    " function and does not contain the necessary `_completion` private"
                    " attribute."
                )
            else:
                open_ai_chat_completion = completion._completion
        dump = open_ai_chat_completion.dump()
        span = Trace(
            name=self.__class__.__name__,
            kind=self.span_type,
            status_code="success",
            status_message=None,
            metadata={
                "call_params": dict(self.call_params),
                "usage": dict(open_ai_chat_completion.completion.usage),  # type: ignore
            },
            start_time_ms=dump["start_time"],
            end_time_ms=dump["end_time"],
            inputs={message["role"]: message["content"] for message in self.messages},
            outputs=output,
        )
        parent.add_child(span)
        return span

    def trace_error(self, error: Exception, parent: Trace) -> Trace:
        """Returns an error trace connected to parent.

        Start time is set to time of prompt creation, and end time is set to the time
        function is called.

        Args:
            error: The error to trace.
            parent: The parent trace to connect to.

        Returns:
            The created error trace, connected to the parent.
        """
        span = Trace(
            name=self.__class__.__name__,
            kind=self.span_type,
            status_code="error",
            status_message=str(error),
            metadata={"call_params": dict(self.call_params)},
            start_time_ms=self._creation_time_ms,
            end_time_ms=round(datetime.datetime.now().timestamp() * 1000),
            inputs={message["role"]: message["content"] for message in self.messages},
            outputs=None,
        )
        parent.add_child(span)
        return span
