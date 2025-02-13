"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from typing import TYPE_CHECKING

from google.generativeai.types.content_types import ToolConfigType
from google.generativeai.types.safety_types import SafetySettingOptions
from pydantic import ConfigDict, with_config
from typing_extensions import NotRequired

from ..base import BaseCallParams

if TYPE_CHECKING:
    from google.generativeai.types import (
        GenerationConfig,
        GenerationConfigDict,
        RequestOptions,
    )
else:
    from google.generativeai.types import (
        GenerationConfig as _GenerationConfig,
    )
    from google.generativeai.types import GenerationConfigDict as _GenerationConfigDict
    from google.generativeai.types import RequestOptions as _RequestOptions

    @with_config(ConfigDict(arbitrary_types_allowed=True))
    class GenerationConfigDict(_GenerationConfigDict): ...

    class GenerationConfig(_GenerationConfig):
        __pydantic_config__ = ConfigDict(arbitrary_types_allowed=True)

    class RequestOptions(_RequestOptions):
        __pydantic_config__ = ConfigDict(arbitrary_types_allowed=True)


class GeminiCallParams(BaseCallParams):
    """The parameters to use when calling the Gemini API.

    [Gemini API Reference](https://ai.google.dev/gemini-api/docs/text-generation?lang=python)

    Attributes:
        generation_config: ...
        safety_settings: ...
        request_options: ...
        tool_config: ...
    """

    generation_config: NotRequired[GenerationConfigDict | GenerationConfig]
    safety_settings: NotRequired[SafetySettingOptions]
    request_options: NotRequired[RequestOptions]
    tool_config: NotRequired[ToolConfigType]
