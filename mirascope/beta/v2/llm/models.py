"""Model interfaces for LLM interactions."""

from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TypeVar, overload

from typing_extensions import TypedDict

from .messages import Message
from .response_formatting import ResponseFormat
from .responses import Response
from .streams import AsyncStream, Stream
from .tools import ToolDef

T = TypeVar("T")


class CallParams(TypedDict, total=False):
    """Parameters for model calls.

    This class defines the parameters that can be used to configure the behavior of
    LLM models during generation. It includes parameters such as temperature, max
    tokens, top_p, and frequency penalty.

    All parameters are optional and model-specific defaults will be used for any
    parameters not explicitly provided.
    """

    temperature: float
    """Controls randomness in the output. Higher values (e.g., 0.8) make the output more random, 
    while lower values (e.g., 0.2) make it more deterministic. Typically ranges from 0 to 1."""

    max_tokens: int
    """The maximum number of tokens to generate in the response."""

    top_p: float
    """An alternative to temperature, used for nucleus sampling. Only the most likely tokens 
    with probabilities that add up to top_p or higher are considered. Typically ranges from 0 to 1."""

    frequency_penalty: float
    """Reduces the likelihood of repetition by penalizing tokens that have already appeared 
    in the text. Higher values increase the penalty. Typically ranges from 0 to 2."""

    presence_penalty: float
    """Reduces the likelihood of repetition by penalizing tokens based on whether they've 
    appeared in the text at all. Higher values increase the penalty. Typically ranges from 0 to 2."""


@dataclass
class Model:
    """The base interface for LLM models.

    This class defines the interface for interacting with language models from
    various providers. It handles the common operations like generating responses,
    streaming, and async variants of these operations.

    Implementations of this class for specific providers should extend it and
    implement the abstract methods for generation and streaming.
    """

    provider: str
    """The provider of the model (e.g., 'google', 'openai', 'anthropic', etc.)."""

    name: str
    """The name of the model (e.g., 'gpt-4', 'claude-3-opus', 'gemini-pro')."""

    params: CallParams
    """The parameters used for model calls (temperature, max_tokens, etc.)."""

    client: object
    """The client object used to interact with the model API."""

    @overload
    def generate(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
    ) -> Response:
        """Overload for generation when there's no response format specified."""
        ...

    @overload
    def generate(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T],
    ) -> Response[T]:
        """Overload for generation when a response format is specified."""
        ...

    @abstractmethod
    def generate(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T] | None = None,
    ) -> Response | Response[T]:
        """Generate a response using the model."""
        ...

    @overload
    async def generate_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
    ) -> Response:
        """Overload for async generation when there's no response format specified."""
        ...

    @overload
    async def generate_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T],
    ) -> Response[T]:
        """Overload for async generation when a response format is specified."""
        ...

    @abstractmethod
    async def generate_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T] | None = None,
    ) -> Response | Response[T]:
        """Generate a response asynchronously using the model."""
        ...

    @overload
    def stream(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
    ) -> Stream:
        """Overload for streaming when there's no response format specified."""
        ...

    @overload
    def stream(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T],
    ) -> Stream[T]:
        """Overload for streaming when a response format is specified."""
        ...

    @abstractmethod
    def stream(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T] | None = None,
    ) -> Stream | Stream[T]:
        """Stream a response using the model."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: None = None,
    ) -> AsyncStream:
        """Overload for async streaming when there's no response format specified."""
        ...

    @overload
    async def stream_async(
        self,
        *,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T],
    ) -> AsyncStream[T]:
        """Overload for async streaming when a response format is specified."""
        ...

    @abstractmethod
    async def stream_async(
        self,
        messages: list[Message],
        tools: Sequence[ToolDef] | None = None,
        response_format: ResponseFormat[T] | None = None,
    ) -> AsyncStream | AsyncStream[T]:
        """Stream a response asynchronously using the model."""
        ...


def model(
    model_name: str, *, params: CallParams | None = None, client: object | None = None
) -> Model:
    """Create or use a model with the given name and parameters.

    This function can be used in two ways:
    1. As a context manager: `with llm.model("provider:model-name") as model: ...`
    2. To create a model instance: `my_model = llm.model("provider:model-name")`

    The model_name should be in the format "provider:model-name", where provider
    is one of the supported providers (openai, anthropic, google, etc.) and
    model-name is the specific model to use.

    Args:
        model_name: The name of the model in format "provider:model-name"
            (e.g., "openai:gpt-4", "anthropic:claude-3-opus").
        params: Optional parameters for the model (temperature, max_tokens, etc.).
            If not provided, default parameters will be used.
        client: Optional custom client to use for API requests.
            If not provided, a default client will be created.

    Returns:
        A `Model` instance that can be used to generate responses.

    Example:
        ```python
        from mirascope import llm

        # Use as a context manager
        with llm.model("openai:gpt-4", params={"temperature": 0.7}) as model:
            response = model.generate(
                messages=[
                    llm.system("You are a helpful assistant."),
                    llm.user("What is the capital of France?")
                ]
            )
            print(response.content)

        # Or create a model instance directly
        my_model = llm.model("anthropic:claude-3-sonnet")
        response = my_model.generate(
            messages=[llm.user("Write a haiku about programming.")]
        )
        ```
    """
    raise NotImplementedError()
