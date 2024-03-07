"""Prompts with WandB and OpenAI integration to support logging functionality."""
import datetime
from typing import Callable, Literal, Optional, Type, TypeVar, Union, overload

from pydantic import BaseModel, PrivateAttr
from wandb.sdk.data_types.trace_tree import Trace

from ..base import BaseType
from ..openai import OpenAICallParams, OpenAIChatCompletion, OpenAIPrompt, OpenAITool

BaseTypeT = TypeVar("BaseTypeT", bound=BaseType)
BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


class WandbPrompt(OpenAIPrompt):
    '''Parent class for inherited WandB functionality.

    Use this class's built in `trace` and `trace_error` methods to log traces to WandB.

    Example:

    ```python
    import os
    import wandb
    from mirascope.wandb import WandbPrompt

    wandb.login(key="YOUR_WANDB_API_KEY")
    wandb.init(project="wandb_logged_chain")

    os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

    class HiPrompt(WandbPrompt):
    """{greeting}."""

    greeting: str

    prompt = HiPrompt(
        span_type="llm",
        greeting="Hello",
    )
    completion, span = prompt.create_with_span()

    root_span.log(name="mirascope_trace")
    ```
    '''

    span_type: Literal["tool", "llm", "chain", "agent"]
    _creation_time_ms: int = PrivateAttr(
        default_factory=lambda: round(datetime.datetime.now().timestamp() * 1000)
    )

    call_params = OpenAICallParams(model="gpt-3.5-turbo-0125")

    def create_with_trace(
        self, parent: Optional[Trace] = None
    ) -> tuple[Optional[OpenAIChatCompletion], Trace]:
        """Creates an OpenAI chat completion and logs it via a W&B `Trace`.

        Args:
            parent: The parent trace to connect to.

        Returns:
            A tuple containing the completion and its trace (which has been connected
                to the parent).
        """
        try:
            completion = super().create()
            return completion, self._trace(completion, parent)
        except Exception as e:
            return None, self._trace_error(e, parent)

    @overload
    def extract_with_trace(
        self, schema: Type[BaseTypeT], parent: Optional[Trace], retries: int = 0
    ) -> tuple[BaseTypeT, Trace]:
        ...  # pragma: no cover

    @overload
    def extract_with_trace(
        self, schema: Type[BaseModelT], parent: Optional[Trace], retries: int = 0
    ) -> tuple[BaseModelT, Trace]:
        ...  # pragma: no cover

    @overload
    def extract_with_trace(
        self, schema: Callable, parent: Optional[Trace], retries: int = 0
    ) -> tuple[OpenAITool, Trace]:
        ...  # pragma: no cover

    def extract_with_trace(self, schema, parent=None, retries=0):
        """Calls an OpenAI extraction then logs the result via a W&B `Trace`.

        Args:
            schema: The schema to extract.
            parent: The parent trace to connect to.
            retries: The number of times to retry the extraction.

        Returns:
            A tuple containing the completion and its trace (which has been connected
                to the parent).
        """
        try:
            completion = super().extract(schema, retries)
            return completion, self._trace(completion, parent)
        except Exception as e:
            return None, self._trace_error(e, parent)

    def _trace(
        self,
        completion: Union[OpenAIChatCompletion, BaseModel],
        parent: Optional[Trace],
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
            if completion.tool and self.call_params.tools:
                output = {
                    "assistant": completion.tool.model_dump(),
                    "tool_output": completion.tool.fn(**completion.tool.args),
                }
                print(output)
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
        if parent:
            parent.add_child(span)
        return span

    def _trace_error(self, error: Exception, parent: Optional[Trace]) -> Trace:
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
        if parent:
            parent.add_child(span)
        return span
