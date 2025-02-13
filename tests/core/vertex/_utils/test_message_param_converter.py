from unittest.mock import PropertyMock, patch

import pytest
from google.cloud.aiplatform_v1beta1.types import content as gapic_content_types
from google.cloud.aiplatform_v1beta1.types import tool as gapic_tool_types
from vertexai.generative_models import Content, Part

from mirascope.core.base import ImagePart
from mirascope.core.base.message_param import (
    BaseMessageParam,
    DocumentPart,
    ImageURLPart,
    ToolCallPart,
    ToolResultPart,
)
from mirascope.core.vertex._utils._message_param_converter import (
    VertexMessageParamConverter,
    _to_document_part,
    _to_image_part,
)


def test_vertex_convert_parts_image():
    raw_gapic_part = gapic_content_types.Part(
        inline_data=gapic_content_types.Blob(
            mime_type="image/png", data=b"\x89PNG\r\n\x1a\n"
        )
    )
    part = Part._from_gapic(raw_gapic_part)
    message = Content(role="assistant", parts=[part])
    with patch.object(Part, "text", new_callable=PropertyMock(return_value="")):
        results = VertexMessageParamConverter.from_provider([message])
        assert len(results) == 1
        result = results[0]
        assert isinstance(result.content, list)
        assert len(result.content) == 1
        assert isinstance(result.content[0], ImagePart)
        assert result.content[0].media_type == "image/png"
        assert result.content[0].image == b"\x89PNG\r\n\x1a\n"
        assert result.role == "assistant"


def test_vertex_convert_parts_image_url():
    raw_gapic_part = gapic_content_types.Part(
        file_data=gapic_content_types.FileData(
            mime_type="image/png", file_uri="https://example.com/image.png"
        )
    )
    part = Part._from_gapic(raw_gapic_part)
    message = Content(role="assistant", parts=[part])
    with patch.object(Part, "text", new_callable=PropertyMock(return_value="")):
        results = VertexMessageParamConverter.from_provider([message])
        assert len(results) == 1
        result = results[0]
        assert isinstance(result.content, list)
        assert len(result.content) == 1
        assert isinstance(result.content[0], ImageURLPart)
        assert result.content[0].url == "https://example.com/image.png"
        assert result.role == "assistant"


def test_vertex_convert_parts_unsupported_image():
    raw_gapic_part = gapic_content_types.Part(
        inline_data=gapic_content_types.Blob(mime_type="image/tiff", data=b"fake")
    )
    part = Part._from_gapic(raw_gapic_part)
    message = Content(role="assistant", parts=[part])
    with (
        patch.object(Part, "text", new_callable=PropertyMock(return_value="")),
        pytest.raises(
            ValueError,
            match="Unsupported inline_data mime type: image/tiff. Cannot convert to BaseMessageParam.",
        ),
    ):
        VertexMessageParamConverter.from_provider([message])


def test_vertex_convert_parts_inline_data_pdf():
    raw_gapic_part = gapic_content_types.Part(
        inline_data=gapic_content_types.Blob(
            mime_type="application/pdf", data=b"%PDF-1.4..."
        )
    )
    part = Part._from_gapic(raw_gapic_part)
    message = Content(role="assistant", parts=[part])
    results = VertexMessageParamConverter.from_provider([message])
    assert len(results) == 1
    assert results == [
        BaseMessageParam(
            role="assistant",
            content=[
                DocumentPart(
                    type="document",
                    media_type="application/pdf",
                    document=b"%PDF-1.4...",
                )
            ],
        )
    ]


def test_vertex_convert_parts_unsupported_inline_data():
    raw_gapic_part = gapic_content_types.Part(
        inline_data=gapic_content_types.Blob(mime_type="application/json", data=b"{}")
    )
    part = Part._from_gapic(raw_gapic_part)
    message = Content(role="assistant", parts=[part])
    with (
        patch.object(Part, "text", new_callable=PropertyMock(return_value="")),
        pytest.raises(
            ValueError,
            match="Unsupported inline_data mime type: application/json. Cannot convert to BaseMessageParam.",
        ),
    ):
        VertexMessageParamConverter.from_provider([message])


def test_to_image_part_unsupported_image():
    with pytest.raises(
        ValueError,
        match="Unsupported image media type: application/json. Expected one of: image/jpeg, image/png, image/gif, image/webp.",
    ):
        _to_image_part(mime_type="application/json", data=b"{}")


def test_to_document_part_unsupported_document():
    with pytest.raises(
        ValueError,
        match="Unsupported document media type: application/json. Only application/pdf is supported.",
    ):
        _to_document_part(mime_type="application/json", data=b"{}")


def test_vertex_convert_parts_tool_result():
    raw_gapic_part = gapic_content_types.Part(
        function_call=gapic_tool_types.FunctionCall(
            name="test", args={"arg1": "value1"}
        )
    )
    part = Part._from_gapic(raw_gapic_part)
    message = Content(role="assistant", parts=[part])
    with patch.object(Part, "text", new_callable=PropertyMock(return_value="")):
        results = VertexMessageParamConverter.from_provider([message])
        assert len(results) == 1
        result = results[0]
        assert result.role in ("assistant", "tool")
        assert len(result.content) == 1
        part_call = result.content[0]
        assert isinstance(part_call, ToolCallPart)
        assert part_call.type == "tool_call"
        assert part_call.name == "test"
        assert part_call.args == {"arg1": "value1"}


def test_gemini_convert_parts_document():
    """
    If file_data is a PDF, produce a DocumentPart.
    """
    part = gapic_content_types.Part(
        file_data=gapic_content_types.FileData(
            mime_type="application/pdf", file_uri=b"%PDF-1.4..."
        )
    )
    with pytest.raises(
        ValueError,
        match='FileData.file_uri is not support: mime_type: "application/pdf"\nfile_uri: "%PDF-1.4..."\n. Cannot convert to BaseMessageParam.',
    ):
        VertexMessageParamConverter.from_provider(
            [Content(role="user", parts=[Part._from_gapic(part)])]
        )


def test_to_provider():
    """
    If there's no content but tool_calls, we only get ToolCallParts in the final list.
    """
    message_param = Content(
        role="assistant",
        parts=[
            Part.from_text("This is a message"),
        ],
    )
    results = VertexMessageParamConverter.to_provider([message_param])  # pyright: ignore [reportArgumentType]
    assert len(results) == 1
    assert results[0].role == "assistant"
    assert results[0].parts[0].text == "This is a message"


def test_function_response():
    raw_gapic_part = gapic_content_types.Part(
        function_response=gapic_tool_types.FunctionResponse(
            name="test", response={"result": "value"}
        )
    )
    part = Part._from_gapic(raw_gapic_part)
    message = Content(role="assistant", parts=[part])
    results = VertexMessageParamConverter.from_provider([message])
    assert len(results) == 1
    assert results == [
        BaseMessageParam(
            role="assistant",
            content=[
                ToolResultPart(
                    type="tool_result",
                    name="test",
                    content="value",
                    id=None,
                    is_error=False,
                )
            ],
        )
    ]
