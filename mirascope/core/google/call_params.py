"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ConfigDict, with_config
from typing_extensions import NotRequired

from ..base import BaseCallParams

if TYPE_CHECKING:
    from google.genai.types import (
        GenerationConfig,
        GenerationConfigDict,
        # RequestOptions,
        SafetySetting,
        ToolConfigOrDict,
    )
else:
    from google.genai.types import (
        GenerationConfig as _GenerationConfig,
    )
    from google.genai.types import GenerationConfigDict as _GenerationConfigDict
    # from google.genai.types import RequestOptions as _RequestOptions

    @with_config(ConfigDict(arbitrary_types_allowed=True))
    class GenerationConfigDict(_GenerationConfigDict): ...

    class GenerationConfig(_GenerationConfig):
        __pydantic_config__ = ConfigDict(arbitrary_types_allowed=True)

    # class RequestOptions(_RequestOptions):
    #     __pydantic_config__ = ConfigDict(arbitrary_types_allowed=True)


class GoogleCallParams(BaseCallParams):
    """The parameters to use when calling the Google API.

    [Google API Reference](https://ai.google.dev/google-api/docs/text-generation?lang=python)

    Attributes:
        generation_config: ...
        safety_settings: ...
        request_options: ...
        tool_config: ...
    """

    generation_config: NotRequired[GenerationConfigDict | GenerationConfig]
    safety_settings: NotRequired[SafetySetting]
    # request_options: NotRequired[RequestOptions]
    tool_config: NotRequired[ToolConfigOrDict]
