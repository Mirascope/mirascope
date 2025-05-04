"""Tests the Mistral OCR decorator and response model."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mistralai.async_client import MistralAsyncClient
from mistralai.client import MistralClient
from mistralai.models.documenturlchunk import DocumentURLChunk
from mistralai.models.ocrimageobject import OCRImageObject as MistralOCRImage # Correct import
from mistralai.models.ocrpageobject import OCRPageObject as MistralOCRPage
from mistralai.models.ocrpagedimensions import OCRPageDimensions # Import Dimensions
from mistralai.models.ocrresponse import OCRResponse as MistralOCRResponse
from mistralai.models.sdkerror import SDKError as MistralException
from pytest_mock import MockerFixture

from mirascope.core.mistral import OCRResponse, ocr


@pytest.fixture()
def fixture_mistral_ocr_response() -> MistralOCRResponse:
    """Returns a mock Mistral OCRResponse."""
    # Adjusted fields to match OCRPageObject model (index, markdown)
    return MistralOCRResponse(
        id="ocr_id",
        object="ocr_result",
        usage=None,
        pages=[
            MistralOCRPage(
                index=0, # Changed from page_number=1
                markdown="Page 1 content\n", # Changed from text_content
                images=[],
                dimensions=None,
            ),
            MistralOCRPage(
                index=1, # Changed from page_number=2
                markdown="Page 2 content\n", # Changed from text_content
                images=[],
                dimensions=None,
            ),
        ],
    )

def test_ocr_response_properties(
    fixture_mistral_ocr_response: MistralOCRResponse,
) -> None:
    """Tests the properties of the Mirascope OCRResponse wrapper."""
    response = OCRResponse(response=fixture_mistral_ocr_response)
    # Accessing markdown field correctly now
    assert response.full_text == "Page 1 content\n\nPage 2 content\n"
    assert len(response.pages) == 2
    assert response.pages[0].markdown == "Page 1 content\n"
    assert response.content == ""  # content property is usually for chat response text
    assert response.id == "ocr_id"
    assert response.response == fixture_mistral_ocr_response

@patch("mirascope.core.mistral._ocr.MistralClient", new_callable=MagicMock)
def test_ocr_sync_url(
    mock_client_class: MagicMock,
    mocker: MockerFixture,
    fixture_mistral_ocr_response: MistralOCRResponse,
) -> None:
    """Tests the ocr decorator with synchronous function returning a URL string."""
    mocker.patch("mirascope.core.mistral._ocr.os.environ.get", return_value="test_key")
    mock_client_instance = mock_client_class.return_value
    mock_client_instance.ocr.process.return_value = fixture_mistral_ocr_response

    @ocr
    def my_ocr_func() -> str:
        return "https://example.com/document.pdf"

    result = my_ocr_func()

    assert isinstance(result, OCRResponse)
    assert result.id == "ocr_id"
    mock_client_instance.ocr.process.assert_called_once_with(
        document=DocumentURLChunk(document_url="https://example.com/document.pdf")
    )

@patch("mirascope.core.mistral._ocr.MistralAsyncClient", new_callable=AsyncMock)
@pytest.mark.anyio
async def test_ocr_async_url(
    mock_async_client_class: AsyncMock,
    mocker: MockerFixture,
    fixture_mistral_ocr_response: MistralOCRResponse,
) -> None:
    """Tests the ocr decorator with asynchronous function returning a URL string."""
    mocker.patch("mirascope.core.mistral._ocr.os.environ.get", return_value="test_key")
    mock_async_client_instance = mock_async_client_class.return_value
    mock_async_client_instance.ocr.process.return_value = fixture_mistral_ocr_response

    @ocr
    async def my_ocr_func() -> str:
        return "https://example.com/async_doc.pdf"

    result = await my_ocr_func()

    assert isinstance(result, OCRResponse)
    assert result.id == "ocr_id"
    mock_async_client_instance.ocr.process.assert_called_once_with(
        document=DocumentURLChunk(document_url="https://example.com/async_doc.pdf")
    )

def test_ocr_invalid_source_type_bytes(mocker: MockerFixture) -> None:
    """Tests that a TypeError is raised for bytes return type."""
    mocker.patch("mirascope.core.mistral._ocr.os.environ.get", return_value="test_key")

    @ocr
    def my_ocr_func() -> bytes:
        return b"some bytes"

    with pytest.raises(
        TypeError, match="Unsupported document source type. Must be a URL string"
    ):
        my_ocr_func()

def test_ocr_invalid_source_type_path(mocker: MockerFixture) -> None:
    """Tests that a TypeError is raised for file path return type."""
    mocker.patch("mirascope.core.mistral._ocr.os.environ.get", return_value="test_key")

    @ocr
    def my_ocr_func() -> str:
        return "/path/to/file.pdf" # Not a URL

    with pytest.raises(
        TypeError, match="Unsupported document source type. Must be a URL string"
    ):
        my_ocr_func()

def test_ocr_sync_wrong_client_type() -> None:
    """Tests TypeError when sync function gets async client."""
    mock_async_client = AsyncMock(spec=MistralAsyncClient)

    @ocr(client=mock_async_client)
    def my_ocr_func() -> str:
        return "https://example.com/doc.pdf"

    with pytest.raises(TypeError, match="A sync function must be decorated with a sync client."):
        my_ocr_func()

@pytest.mark.anyio
async def test_ocr_async_wrong_client_type() -> None:
    """Tests TypeError when async function gets sync client."""
    mock_sync_client = MagicMock(spec=MistralClient)

    @ocr(client=mock_sync_client)
    async def my_ocr_func() -> str:
        return "https://example.com/doc.pdf"

    with pytest.raises(TypeError, match="An async function must be decorated with an async client."):
        await my_ocr_func()

@patch("mirascope.core.mistral._ocr.MistralClient", new_callable=MagicMock)
def test_ocr_api_error(mock_client_class: MagicMock, mocker: MockerFixture) -> None:
    """Tests that MistralException is raised correctly."""
    mocker.patch("mirascope.core.mistral._ocr.os.environ.get", return_value="test_key")
    mock_client_instance = mock_client_class.return_value
    mock_client_instance.ocr.process.side_effect = MistralException("API Error") # Simplified error

    @ocr
    def my_ocr_func() -> str:
        return "https://example.com/doc.pdf"

    with pytest.raises(MistralException, match="API Error"):
        my_ocr_func()

def test_ocr_no_api_key(mocker: MockerFixture) -> None:
    """Tests ValueError if API key is not set and no client provided."""
    mocker.patch("mirascope.core.mistral._ocr.os.environ.get", return_value=None)  # No key

    @ocr
    def my_ocr_func() -> str:
        return "https://example.com/doc.pdf"

    with pytest.raises(ValueError, match="MISTRAL_API_KEY environment variable must be set"):
        my_ocr_func()

# Test decorator used with arguments
@patch("mirascope.core.mistral._ocr.MistralClient", new_callable=MagicMock)
def test_ocr_sync_url_with_client_arg(
    mock_client_instance: MagicMock,
    fixture_mistral_ocr_response: MistralOCRResponse,
) -> None:
    """Tests the ocr decorator used as @ocr(client=...) with a sync function."""
    mock_client_instance.ocr.process.return_value = fixture_mistral_ocr_response

    @ocr(client=mock_client_instance)
    def my_ocr_func() -> str:
        return "https://example.com/client_arg_doc.pdf"

    result = my_ocr_func()

    assert isinstance(result, OCRResponse)
    assert result.id == "ocr_id"
    mock_client_instance.ocr.process.assert_called_once_with(
        document=DocumentURLChunk(document_url="https://example.com/client_arg_doc.pdf")
    )

# Test decorator used without arguments on async func
@patch("mirascope.core.mistral._ocr.MistralAsyncClient", new_callable=AsyncMock)
@pytest.mark.anyio
async def test_ocr_async_url_no_decorator_args(
    mock_async_client_class: AsyncMock,
    mocker: MockerFixture,
    fixture_mistral_ocr_response: MistralOCRResponse,
) -> None:
    """Tests @ocr used directly on an async function."""
    mocker.patch("mirascope.core.mistral._ocr.os.environ.get", return_value="test_key")
    mock_async_client_instance = mock_async_client_class.return_value
    mock_async_client_instance.ocr.process.return_value = fixture_mistral_ocr_response

    @ocr  # No parentheses
    async def my_ocr_func() -> str:
        return "https://example.com/async_no_args.pdf"

    result = await my_ocr_func()

    assert isinstance(result, OCRResponse)
    assert result.id == "ocr_id"
    mock_async_client_instance.ocr.process.assert_called_once_with(
        document=DocumentURLChunk(document_url="https://example.com/async_no_args.pdf")
    )

# Test the fixture itself (simple check)
def test_fixture_mistral_ocr_response_type(
    fixture_mistral_ocr_response: MistralOCRResponse,
) -> None:
    assert isinstance(fixture_mistral_ocr_response, MistralOCRResponse)
    assert len(fixture_mistral_ocr_response.pages) == 2
    assert fixture_mistral_ocr_response.pages[0].index == 0
    assert fixture_mistral_ocr_response.pages[0].markdown == "Page 1 content\n"
