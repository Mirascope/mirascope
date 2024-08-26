from collections.abc import AsyncGenerator, Callable, Generator
from typing import Any, ClassVar, Generic, TypeVar

from pydantic import model_validator
from tenacity import AsyncRetrying, Retrying
from typing_extensions import Self

from ...core.base import (
    BaseCallResponse,
    BaseCallResponseChunk,
    BasePrompt,
    BaseTool,
    _utils,
)
from ...core.base.dynamic_config import DynamicConfigFull
from .types import BaseCallParams
from .utils import retry_decorator

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)


class BaseCall(
    BasePrompt, Generic[_BaseCallResponseT, _BaseCallResponseChunkT, _BaseToolT]
):
    tags: ClassVar[list[str]] = []
    prompt_template: ClassVar[str] = ""

    call_params: ClassVar[BaseCallParams] = BaseCallParams(model="")

    _decorator: ClassVar[Callable] = lambda self: None
    _provider: ClassVar[str] = "NO PROVIDER"

    @model_validator(mode="after")
    def set_prompt_template(self) -> Self:
        self._prompt_template = self.prompt_template
        return self

    def dynamic_config(self) -> DynamicConfigFull:
        """Returns the dynamic configuration set from user provided information."""
        config: DynamicConfigFull = {
            "call_params": self.call_params.model_dump(exclude={"model", "tools"}),
            "tools": [
                tool
                if isinstance(tool, type)
                else _utils.convert_function_to_base_tool(tool, BaseTool)
                for tool in self.call_params.tools or []
            ],
        }
        if hasattr(self, "messages"):
            config["messages"] = self.messages()  # pyright: ignore [reportAttributeAccessIssue]
        return config

    def dump(
        self,
    ) -> dict[str, Any]:
        """Dumps the contents of the prompt into a dictionary."""
        return {
            "tags": self.tags,
            "template": _utils.get_prompt_template(self),
            "inputs": self.model_dump(),
        }

    def call(
        self,
        retries: int | Retrying = 0,
        client: Any | None = None,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> _BaseCallResponseT:
        """A call to an LLM."""
        return self.run(
            self.__class__._decorator(self.call_params.model, client=client),
            retry_decorator(retries),
        )  # pyright: ignore [reportReturnType]

    async def call_async(
        self,
        retries: int | AsyncRetrying = 0,
        client: Any | None = None,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> _BaseCallResponseT:
        """An asynchronous call to an LLM."""
        return await self.run_async(
            self.__class__._decorator(self.call_params.model, client=client),
            retry_decorator(retries),
        )  # pyright: ignore [reportReturnType]

    def stream(
        self,
        retries: int | Retrying = 0,
        client: Any | None = None,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> Generator[tuple[_BaseCallResponseChunkT, _BaseToolT], None, None]:
        """A call to an LLM that streams the response in chunks."""
        yield from self.run(
            self.__class__._decorator(
                self.call_params.model, stream=True, client=client
            ),
            retry_decorator(retries),
        )  # pyright: ignore [reportReturnType]

    async def stream_async(
        self,
        retries: int | AsyncRetrying = 0,
        client: Any | None = None,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> AsyncGenerator[tuple[_BaseCallResponseChunkT, _BaseToolT], None]:
        """A asynchronous call to an LLM that streams the response in chunks."""
        async for chunk, tool in self.run_async(  # pyright: ignore [reportGeneralTypeIssues]
            self.__class__._decorator(
                self.call_params.model, stream=True, client=client
            ),
            retry_decorator(retries),
        ):
            yield chunk, tool
