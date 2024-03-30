"""Prompts with WandB and OpenAI integration to support logging functionality."""
from __future__ import annotations

import datetime
from abc import abstractmethod
from typing import (
    Any,
    AsyncGenerator,
    ClassVar,
    Generator,
    Generic,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
)

from pydantic import BaseModel
from wandb.sdk.data_types.trace_tree import Trace

from ..base import (
    BaseCallResponse,
    BasePrompt,
    BaseTool,
    BaseType,
    ExtractedType,
    ExtractionType,
)

BaseTypeT = TypeVar("BaseTypeT", bound=BaseType)
BaseModelT = TypeVar("BaseModelT", bound=BaseModel)
BaseCallResponseT = TypeVar("BaseCallResponseT", bound=BaseCallResponse)


class _WandbBaseCall(BasePrompt):
    span_type: Literal["tool", "llm", "chain", "agent"]

    api_key: ClassVar[Optional[str]] = None
    base_url: ClassVar[Optional[str]] = None
    call_params: ClassVar[Any]

    @abstractmethod
    def call(self, **kwargs: Any) -> Any:
        ...  # pragma: no cover

    @abstractmethod
    async def call_async(self, **kwargs: Any) -> Any:
        ...  # pragma: no cover

    @abstractmethod
    def stream(self, **kwargs: Any) -> Generator[Any, None, None]:
        ...  # pragma: no cover

    @abstractmethod
    async def stream_async(self, **kwargs: Any) -> AsyncGenerator[Any, None]:
        yield ...  # type: ignore # pragma: no cover


class _WandbBaseExtractor(BasePrompt):
    span_type: Literal["tool", "llm", "chain", "agent"]

    extract_schema: ExtractionType

    api_key: ClassVar[Optional[str]] = None
    base_url: ClassVar[Optional[str]] = None
    call_params: ClassVar[Any]

    @abstractmethod
    def extract(self, retries: int = 0) -> ExtractedType:
        """Extracts the `extraction_schema` from an LLM call."""
        ...  # pragma: no cover

    @abstractmethod
    async def extract_async(self, retries: int = 0) -> ExtractedType:
        """Asynchronously extracts the `extraction_schema` from an LLM call."""
        ...  # pragma: no cover


def trace(
    call: Union[_WandbBaseCall, _WandbBaseExtractor],
    response: BaseCallResponse,
    tool_type: Optional[Type[BaseTool]],
    parent: Optional[Trace],
    **kwargs: Any,
) -> Trace:
    """Returns a trace connected to parent.

    Args:
        response: The response to trace. Handles `BaseCallResponse` for call/stream, and
            `BaseModel` for extractions.
        tool_type: The `BaseTool` provider-specific tool type e.g. `OpenAITool`
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
        "call_params": call.call_params.model_copy(update=kwargs).kwargs(tool_type)
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
    call: Union[_WandbBaseCall, _WandbBaseExtractor],
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


class WandbCallMixin(_WandbBaseCall, Generic[BaseCallResponseT]):
    '''A mixin for integrating a call with Weights & Biases.

    Use this class's built in `call_with_trace` method to log traces to WandB along with
    your calls to LLM. These calls will include all of the additional metadata
    information such as the prompt template, template variables, and more.

    Example:

    ```python
    import os

    from mirascope.openai import OpenAICall, OpenAICallResponse
    from mirascope.wandb import WandbCallMixin
    import wandb

    wandb.login(key="YOUR_WANDB_API_KEY")
    wandb.init(project="wandb_logged_chain")

    os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


    class BookRecommender(OpenAICall, WandbCallMixin[OpenAICallResponse]):
        prompt_template = """
        SYSTEM:
        You are the world's greatest librarian.

        USER:
        Please recommend a {genre} book.
        """

        genre: str


    recommender = BookRecommender(span_type="llm", genre="fantasy")
    response, span = recommender.call_with_trace()
    #           ^ this is a `Span` returned from the trace (or trace error).
    ```
    '''

    span_type: Literal["tool", "llm", "chain", "agent"]

    def call_with_trace(
        self,
        parent: Optional[Trace] = None,
        **kwargs: Any,
    ) -> tuple[Optional[BaseCallResponseT], Trace]:
        """Creates an LLM response and logs it via a W&B `Trace`.

        Args:
            parent: The parent trace to connect to.

        Returns:
            A tuple containing the completion and its trace (which has been connected
                to the parent).
        """
        try:
            start_time = datetime.datetime.now().timestamp() * 1000
            response = self.call(**kwargs)
            tool_type = None
            if response.tool_types and len(response.tool_types) > 0:
                tool_type = response.tool_types[0].__bases__[0]  # type: ignore
            span = trace(self, response, tool_type, parent, **kwargs)
            return response, span  # type: ignore
        except Exception as e:
            return None, trace_error(self, e, parent, start_time, **kwargs)


T = TypeVar("T", bound=ExtractedType)


class WandbExtractorMixin(_WandbBaseExtractor, Generic[T]):
    '''A extractor mixin for integrating with Weights & Biases.

    Use this class's built in `extract_with_trace` method to log traces to WandB along
    with your calls to the LLM. These calls will include all of the additional metadata
    information such as the prompt template, template variables, and more.

    Example:

    ```python
    import os
    from typing import Type

    from mirascope.openai import OpenAIExtractor
    from mirascope.wandb import WandbExtractorMixin
    from pydantic import BaseModel
    import wandb

    wandb.login(key="YOUR_WANDB_API_KEY")
    wandb.init(project="wandb_logged_chain")

    os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


    class Book(BaseModel):
        title: str
        author: str


    class BookRecommender(OpenAIExtractor[Book], WandbExtractorMixin[Book]):
        extract_schema: Type[Book] = Book
        prompt_template = """
        SYSTEM:
        You are the world's greatest librarian.

        USER:
        Please recommend a {genre} book.
        """

        genre: str


    recommender = BookRecommender(span_type="tool", genre="fantasy")
    book, span = recommender.extract_with_trace()
    #       ^ this is a `Span` returned from the trace (or trace error).
    ```
    '''

    span_type: Literal["tool", "llm", "chain", "agent"]

    def extract_with_trace(
        self,
        parent: Optional[Trace] = None,
        retries: int = 0,
        **kwargs: Any,
    ) -> tuple[Optional[T], Trace]:
        """Extracts `extract_schema` from the LLM call response and traces it.

        The `extract_schema` is converted into an tool, complete with a description of
        the tool, all of the fields, and their types. This allows us to take advantage
        of tool/function calling functionality to extract information from a response
        according to the context provided by the `BaseModel` schema.

        Args:
            parent: The parent trace to connect to.
            retries: The maximum number of times to retry the query on validation error.
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            The `Schema` instance extracted from the response and it's trace.
        """
        try:
            start_time = datetime.datetime.now().timestamp() * 1000
            model = self.extract(retries=retries, **kwargs)
            span = trace(self, model._response, parent, **kwargs)  # type: ignore
            return model, span  # type: ignore
        except Exception as e:
            return None, trace_error(self, e, parent, start_time, **kwargs)
