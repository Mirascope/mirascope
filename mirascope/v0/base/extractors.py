from collections.abc import AsyncGenerator, Callable, Generator
from typing import Any, ClassVar, Generic, TypeVar

from pydantic import BaseModel, model_validator
from tenacity import AsyncRetrying, Retrying
from typing_extensions import Self

from ...core.base import BasePrompt, BaseTool, _utils
from ...core.base.dynamic_config import DynamicConfigFull
from .types import BaseCallParams
from .utils import retry_decorator

ExtractedType = _utils.BaseType | BaseModel
_ExtractedTypeT = TypeVar("_ExtractedTypeT", bound=ExtractedType)


class BaseExtractor(BasePrompt, Generic[_ExtractedTypeT]):
    extract_schema: type[_utils.BaseType] | type[BaseModel] | Callable
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

    def extract(
        self,
        retries: int | Retrying = 0,
        client: Any | None = None,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> _ExtractedTypeT:
        """Extracts the `extract_schema` format from the response."""
        return self.run(
            self.__class__._decorator(
                self.call_params.model,
                response_model=self.extract_schema,
                client=client,
            ),
            retry_decorator(retries),
        )

    async def extract_async(
        self,
        retries: int | Retrying = 0,
        client: Any | None = None,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> _ExtractedTypeT:
        """Asynchronously extracts the `extract_schema` format from the response."""
        return await self.run_async(
            self.__class__._decorator(
                self.call_params.model,
                response_model=self.extract_schema,
                client=client,
            ),
            retry_decorator(retries),
        )

    def stream(
        self,
        retries: int | Retrying = 0,
        client: Any | None = None,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> Generator[_ExtractedTypeT, None, None]:
        """Streams the desired structured output from the response."""
        yield from self.run(
            self.__class__._decorator(
                self.call_params.model,
                response_model=self.extract_schema,
                stream=True,
                client=client,
            ),
            retry_decorator(retries),
        )

    async def stream_async(
        self,
        retries: int | AsyncRetrying = 0,
        client: Any | None = None,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> AsyncGenerator[_ExtractedTypeT, None]:
        """Asynchronously streams the desired structured output from the response."""
        async for item in await self.run_async(
            self.__class__._decorator(
                self.call_params.model,
                response_model=self.extract_schema,
                stream=True,
                client=client,
            ),
            retry_decorator(retries),
        ):
            yield item
