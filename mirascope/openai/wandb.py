"""Prompts with WandB and OpenAI integration to support logging functionality."""
import datetime
from typing import Any, Literal, Optional, TypeVar

from pydantic import BaseModel
from wandb.sdk.data_types.trace_tree import Trace

from ..base import BaseType
from ..openai import OpenAICall, OpenAICallResponse, OpenAITool

BaseTypeT = TypeVar("BaseTypeT", bound=BaseType)
BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


class WandbOpenAICall(OpenAICall):
    '''An `OpenAICall` with added convenience for integrating with Weights & Biases.

    Use this class's built in `call_with_trace` method to log traces to WandB along with
    your calls to OpenAI. These calls will include all of the additional metadata
    information such as the prompt template, template variables, and more.

    Example:

    ```python
    import os

    from mirascope.wandb.openai import WandbOpenAICall
    import wandb

    wandb.login(key="YOUR_WANDB_API_KEY")
    wandb.init(project="wandb_logged_chain")

    os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


    class BookRecommender(WandbOpenAICall):
        template = """
        SYSTEM:
        You are the world's greatest librarian.

        USER:
        Please recommend a {genre} book.
        """

        genre: str


    response, span = BookRecommender(genre="fantasy").call_with_trace()
    #           ^ this is a `Span` returned from the trace (or trace error).
    ```
    '''

    span_type: Literal["tool", "llm", "chain", "agent"]

    def call_with_trace(
        self,
        parent: Optional[Trace] = None,
        **kwargs: Any,
    ) -> tuple[Optional[OpenAICallResponse], Trace]:
        """Creates an OpenAI chat completion and logs it via a W&B `Trace`.

        Args:
            parent: The parent trace to connect to.

        Returns:
            A tuple containing the completion and its trace (which has been connected
                to the parent).
        """
        try:
            start_time = datetime.datetime.now().timestamp() * 1000
            response = super().call()
            span = self._trace(response, parent, **kwargs)
            return response, span
        except Exception as e:
            return None, self._trace_error(e, parent, start_time, **kwargs)

    def _trace(
        self,
        response: OpenAICallResponse,
        parent: Optional[Trace],
        **kwargs: Any,
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
        tool = response.tool
        if tool is not None:
            outputs = {
                "assistant": tool.model_dump(),
                "tool_output": tool.fn(**tool.args),
            }
        else:
            outputs = {"assistant": response.content}

        metadata = {
            "call_params": self.call_params.model_copy(update=kwargs).kwargs(OpenAITool)
        }
        if response.response.usage is not None:
            metadata["usage"] = response.response.usage.model_dump()
        span = Trace(
            name=self.__class__.__name__,
            kind=self.span_type,
            status_code="success",
            status_message=None,
            metadata=metadata,
            start_time_ms=round(response.start_time),
            end_time_ms=round(response.end_time),
            inputs={message["role"]: message["content"] for message in self.messages()},
            outputs=outputs,
        )
        if parent:
            parent.add_child(span)
        return span

    def _trace_error(
        self,
        error: Exception,
        parent: Optional[Trace],
        start_time: float,
        **kwargs: Any,
    ) -> Trace:
        """Returns an error trace connected to parent.

        Start time is set to time of prompt creation, and end time is set to the time
        function is called.

        Args:
            error: The error to trace.
            parent: The parent trace to connect to.
            start_time: The time the call to OpenAI was started.

        Returns:
            The created error trace, connected to the parent.
        """
        span = Trace(
            name=self.__class__.__name__,
            kind=self.span_type,
            status_code="error",
            status_message=str(error),
            metadata={
                "call_params": self.call_params.model_copy(update=kwargs).kwargs()
            },
            start_time_ms=round(start_time),
            end_time_ms=round(datetime.datetime.now().timestamp() * 1000),
            inputs={message["role"]: message["content"] for message in self.messages()},
            outputs=None,
        )
        if parent:
            parent.add_child(span)
        return span
