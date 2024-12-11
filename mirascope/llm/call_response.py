from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypeVar

from pydantic import BaseModel, computed_field, model_validator

from mirascope.core.base import BaseCallResponse
from mirascope.core.base.call_params import BaseCallParams
from mirascope.core.base.message_param import BaseMessageParam
from mirascope.core.base.tool import BaseTool
from mirascope.llm._get_provider_converter import _get_provider_converter

if TYPE_CHECKING:
    from mirascope.llm._base_provider_converter import BaseProviderConverter

_ResponseT = TypeVar("_ResponseT", bound=Any)

Provider = Literal["openai", "anthropic"]


class Usage(BaseModel):
    completion_tokens: int
    """Number of tokens in the generated completion."""

    prompt_tokens: int
    """Number of tokens in the prompt."""

    total_tokens: int
    """Total number of tokens used in the request (prompt + completion)."""


class CallResponse(
    BaseCallResponse[
        _ResponseT,
        BaseTool,
        object,
        Any,
        BaseMessageParam,
        BaseCallParams,
        BaseMessageParam,
    ]
):
    """
    A provider-agnostic CallResponse with a single generic parameter.

    Example usage:
    CallResponse[ChatCompletion]
    """

    provider: Provider
    provider_call_response: BaseCallResponse
    _message_param: BaseMessageParam
    _usage: Usage

    @model_validator(mode="before")
    def _pre_init_validate(cls, values: Any) -> Any:  # noqa: ANN401
        if (provider := values.get("provider")) and (provider_converter := _get_provider_converter(provider)):
            provider_call_response = (
                provider_converter.get_call_response_class().model_validate(values)
            )
            return {
                **values,
                "provider_call_response": provider_call_response,
                "provider": provider,
            }
        raise ValueError("Invalid provider")

    @model_validator(mode="after")
    def _post_init_normalize(self) -> CallResponse[_ResponseT]:
        if provider_converter := _get_provider_converter(self.provider):
            self._message_param = provider_converter.get_message_param(
                self.provider_call_response.message_param
            )
            self._usage = provider_converter.get_usage(
                self.provider_call_response.usage
            )
        return self

    @property
    def content(self) -> str:
        return self.provider_call_response.content

    @property
    def finish_reasons(self) -> list[str] | None:
        return self.provider_call_response.finish_reasons

    @property
    def model(self) -> str | None:
        return self.provider_call_response.model

    @property
    def id(self) -> str | None:
        return self.provider_call_response.id

    @property
    def usage(self) -> object | None:
        return self._usage

    @property
    def input_tokens(self) -> int | float | None:
        return self.provider_call_response.input_tokens

    @property
    def output_tokens(self) -> int | float | None:
        return self.provider_call_response.output_tokens

    @property
    def cost(self) -> float | None:
        return self.provider_call_response.cost

    @computed_field
    @property
    def message_param(self) -> BaseMessageParam:
        return self._message_param

    @computed_field
    @property
    def tools(self) -> list[BaseTool] | None:
        return self.provider_call_response.tools

    @property
    def tool(self) -> BaseTool | None:
        return self.provider_call_response.tool

    @classmethod
    def tool_message_params(
        cls, tools_and_outputs: list[tuple[BaseTool, str]]
    ) -> list[BaseMessageParam]:
        return [
            BaseMessageParam(role="tool", content=output)
            for _, output in tools_and_outputs
        ]
