"""Prompts with WandB and OpenAI integration to support logging functionality."""
from __future__ import annotations

import datetime
from typing import Any, Generic, Literal, Optional, TypeVar, Union

from pydantic import BaseModel
from wandb.sdk.data_types.trace_tree import Trace

from ..base import BasePrompt, BaseType, ExtractedType
from ..openai import (
    OpenAICall,
    OpenAICallResponse,
    OpenAIExtractor,
    OpenAITool,
)

BaseTypeT = TypeVar("BaseTypeT", bound=BaseType)
BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


def trace(
    call: Union[WandbOpenAICall, WandbOpenAIExtractor],
    response: OpenAICallResponse,
    parent: Optional[Trace],
    **kwargs: Any,
) -> Trace:
    """Returns a trace connected to parent.

    Args:
        response: The completion to trace. Handles `OpenAIChatCompletion` output
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
        "call_params": call.call_params.model_copy(update=kwargs).kwargs(OpenAITool)
    }
    if response.response.usage is not None:
        metadata["usage"] = response.response.usage.model_dump()
    span = Trace(
        name=call.__class__.__name__,
        kind=call.span_type,
        status_code="success",
        status_message=None,
        metadata=metadata,
        start_time_ms=round(response.start_time),
        end_time_ms=round(response.end_time),
        inputs={message["role"]: message["content"] for message in call.messages()},
        outputs=outputs,
    )
    if parent:
        parent.add_child(span)
    return span


def trace_error(
    call: Union[WandbOpenAICall, WandbOpenAIExtractor],
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
        name=call.__class__.__name__,
        kind=call.span_type,
        status_code="error",
        status_message=str(error),
        metadata={"call_params": call.call_params.model_copy(update=kwargs).kwargs()},
        start_time_ms=round(start_time),
        end_time_ms=round(datetime.datetime.now().timestamp() * 1000),
        inputs={message["role"]: message["content"] for message in call.messages()},
        outputs=None,
    )
    if parent:
        parent.add_child(span)
    return span


class WandbBasePrompt(BasePrompt):
    """An extension of `BasePrompt` with Weights & Biases specific functionality."""

    span_type: Literal["tool", "llm", "chain", "agent"]


class WandbOpenAICall(OpenAICall, WandbBasePrompt):
    '''A `OpenAICall` with added convenience for integrating with Weights & Biases.

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
        prompt_template = """
        SYSTEM:
        You are the world's greatest librarian.

        USER:
        Please recommend a {genre} book.
        """

        genre: str


    response, span = BookRecommender(span_type="llm", genre="fantasy").call_with_trace()
    #           ^ this is a `Span` returned from the trace (or trace error).
    ```
    '''

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
            span = trace(self, response, parent, **kwargs)
            return response, span
        except Exception as e:
            return None, trace_error(self, e, parent, start_time, **kwargs)


T = TypeVar("T", bound=ExtractedType)


class WandbOpenAIExtractor(OpenAIExtractor[T], WandbBasePrompt, Generic[T]):
    '''A `OpenAIExtractor` with added convenience for integrating with Weights & Biases.

    Use this class's built in `extract_with_trace` method to log traces to WandB along
    with your calls to OpenAI. These calls will include all of the additional metadata
    information such as the prompt template, template variables, and more.

    Example:

    ```python
    import os
    from typing import Type

    from mirascope.wandb.openai import WandbOpenAIExtractor
    from pydantic import BaseModel
    import wandb

    wandb.login(key="YOUR_WANDB_API_KEY")
    wandb.init(project="wandb_logged_chain")

    os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


    class Book(BaseModel):
        title: str
        author: str


    class BookRecommender(WandbOpenAIExtractor[Book]):
        extract_schema: Type[Book] = Book
        prompt_template = """
        SYSTEM:
        You are the world's greatest librarian.

        USER:
        Please recommend a {genre} book.
        """

        genre: str


    book, span = BookRecommender(span_type="tool", genre="fantasy").extract_with_trace()
    #           ^ this is a `Span` returned from the trace (or trace error).
    ```
    '''

    def extract_with_trace(
        self,
        parent: Optional[Trace] = None,
        retries: int = 0,
        **kwargs: Any,
    ) -> tuple[Optional[T], Trace]:
        """Extracts `extract_schema` from the OpenAI call response and traces it.

        The `extract_schema` is converted into an `OpenAITool`, complete with a
        description of the tool, all of the fields, and their types. This allows us to
        take advantage of OpenAI's tool/function calling functionality to extract
        information from a prompt according to the context provided by the `BaseModel`
        schema.

        Args:
            retries: The maximum number of times to retry the query on validation error.
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            The `Schema` instance extracted from the completion.

        Raises:
            AttributeError: if there is no tool in the call creation.
            ValidationError: if the schema cannot be instantiated from the completion.
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        try:
            start_time = datetime.datetime.now().timestamp() * 1000
            model = super().extract(retries=retries, **kwargs)
            span = trace(self, model._response, parent, **kwargs)  # type: ignore
            return model, span
        except Exception as e:
            return None, trace_error(self, e, parent, start_time, **kwargs)
