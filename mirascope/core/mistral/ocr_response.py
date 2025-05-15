
"""Pydantic models for Mistral OCR responses."""

from typing import List, Optional

from mistralai.models.ocrimageobject import OCRImageObject as OCRImage
from mistralai.models.ocrpageobject import OCRPageObject as OCRPage
from mistralai.models.ocrresponse import OCRResponse as MistralOCRResponse
from pydantic import BaseModel, Field, computed_field


class OCRResponse(BaseModel):
    """A wrapper for the `mistralai.models.ocr.OCRResponse`.

    Provides convenient properties for accessing the response data.
    """

    response: MistralOCRResponse = Field(..., exclude=True)
    """The original `mistralai` OCR response object."""
    pages: List[OCRPage] = Field(..., description="A list of pages in the document.")
    """A list of `OCRPage` objects, each representing a page in the document."""

    @computed_field  # type: ignore
    @property
    def full_text(self) -> str:
        """Returns the concatenated Markdown text content from all pages."""
        return "\n\n".join(page.text_content for page in self.pages)

    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, *, response: MistralOCRResponse, **data):
        """Initializes the OCRResponse, extracting pages from the raw response."""
        super().__init__(response=response, pages=response.pages, **data)


__all__ = ["OCRResponse", "OCRPage", "OCRImage"]
