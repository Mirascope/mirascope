import base64
from typing import Any

from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessageParam,
    ChatCompletionToolMessageParam,
)

from mirascope.core import BaseMessageParam
from mirascope.core.base import (
    AudioPart,
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseStream,
    ImagePart,
    TextPart,
    call_factory,
)
from mirascope.core.openai import (
    OpenAICallParams,
    OpenAICallResponse,
    OpenAICallResponseChunk,
    OpenAIStream,
)
from mirascope.core.openai._utils import (
    get_json_output,
    handle_stream,
    handle_stream_async,
    setup_call,
)
from mirascope.llm._base_provider_converter import BaseProviderConverter
from mirascope.llm.call_response import CallResponse, Usage
from mirascope.llm.call_response_chunk import CallResponseChunk, FinishReason
from mirascope.llm.stream import Stream
from mirascope.llm.tool import Tool

openai_call_factory = call_factory(
    TCallResponse=CallResponse[ChatCompletion],
    TCallResponseChunk=CallResponseChunk[ChatCompletionChunk],
    TToolType=Tool[ChatCompletionToolMessageParam],
    TStream=Stream[ChatCompletionChunk],
    default_call_params=OpenAICallParams(),
    setup_call=setup_call,
    get_json_output=get_json_output,
    handle_stream=handle_stream,
    handle_stream_async=handle_stream_async,
    provider="openai",
)


class OpenAIProviderConverter(BaseProviderConverter):
    @staticmethod
    def get_call_factory() -> Any:
        return openai_call_factory

    @staticmethod
    def get_call_response_chunk_class() -> type[BaseCallResponseChunk]:
        return OpenAICallResponseChunk

    @staticmethod
    def get_usage(usage: Any) -> Usage:
        return Usage.model_validate(usage, from_attributes=True)

    @staticmethod
    def get_call_response_class() -> type[BaseCallResponse]:
        return OpenAICallResponse

    @staticmethod
    def get_chunk_finish_reasons(chunk: BaseCallResponseChunk) -> list[FinishReason]:
        return chunk.finish_reasons

    @staticmethod
    def get_message_param(
        message_param: ChatCompletionMessageParam,
    ) -> BaseMessageParam:
        role = message_param["role"]
        content = message_param.get("content")

        if isinstance(content, str):
            return BaseMessageParam(role=role, content=content)
        else:
            parts = []
            for part_dict in content:
                part_type = part_dict.get("type")

                if part_type == "text":
                    parts.append(TextPart(type="text", text=part_dict["text"]))

                elif part_type == "image_url":
                    image_url = part_dict["image_url"]
                    url = image_url["url"]
                    detail = image_url.get("detail", "auto")
                    media_info, b64data = url.split(",", 1)
                    media_type = media_info.split(":")[1].split(";")[0]
                    image_data = base64.b64decode(b64data)
                    parts.append(
                        ImagePart(
                            type="image",
                            media_type=media_type,
                            image=image_data,
                            detail=detail,
                        )
                    )

                elif part_type == "input_audio":
                    audio_info = part_dict["input_audio"]
                    fmt = audio_info["format"]
                    audio_data = base64.b64decode(audio_info["data"])
                    media_type = f"audio/{fmt}"
                    parts.append(
                        AudioPart(type="audio", media_type=media_type, audio=audio_data)
                    )

                else:
                    raise ValueError(f"Unsupported part type: {part_type}")

            return BaseMessageParam(role=role, content=parts)

    @staticmethod
    def get_stream_class() -> type[BaseStream]:
        return OpenAIStream
