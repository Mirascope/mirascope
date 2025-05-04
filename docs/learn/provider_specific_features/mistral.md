
# Mistral Provider-Specific Features

Mirascope integrates seamlessly with Mistral AI, offering convenient ways to leverage its unique capabilities beyond standard LLM calls. This includes support for Mistral's Optical Character Recognition (OCR) feature.

## OCR with `@mistral.ocr`

Mistral offers a dedicated OCR endpoint (`mistral-ocr-latest`) designed for extracting text and understanding content from documents like PDFs, images, and slides. Mirascope provides the `@mistral.ocr` decorator to simplify interacting with this feature.

### Requirements

- Install the `mistralai` package: `pip install mistralai`
- Set your Mistral API key as an environment variable: `export MISTRAL_API_KEY="YOUR_API_KEY"`

### Usage

The `@mistral.ocr` decorator wraps a function (synchronous or asynchronous) that returns the source of the document to be processed. The source can be:

1.  **Bytes:** Raw byte content of the document.
2.  **URL:** A publicly accessible URL pointing to the document.
3.  **File Path:** A string representing the local path to the document file.

The decorated function will automatically call the Mistral OCR API and return a `mirascope.core.mistral.OCRResponse` object.

### `OCRResponse` Model

The `OCRResponse` object wraps the raw response from the `mistralai` client and provides helpful properties:

- `response`: The original `mistralai.models.ocr.OCRResponse`.
- `full_text`: A string containing the concatenated Markdown text content from all pages, separated by double newlines (`\n\n`).
- `pages`: A list of `mistralai.models.ocr.OCRPage` objects, each containing details like `page_number`, `text_content`, and `images`.
- `pages[i].images`: Each `OCRPage` object within the `pages` list has an `images` attribute. This attribute is a list of `mistralai.models.ocr.OCRImage` objects (containing base64 encoded image data and a prompt) found on that specific page (page `i`). If a page has no images, its `images` list will be empty.

### Examples

!!! note

    Make sure you have `mistralai` installed and `MISTRAL_API_KEY` set in your environment.

=== "Synchronous"

    ```python
    import os
    from pathlib import Path
    from mirascope.core import mistral

    # Ensure MISTRAL_API_KEY is set
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable not set.")

    # Create a dummy PDF file for demonstration
    dummy_pdf_path = Path("dummy_document.pdf")
    # In a real scenario, you'd need a library like reportlab or have an actual PDF
    # For this example, we just create an empty file to demonstrate path handling.
    # The API call will likely fail without a valid PDF, but the decorator logic works.
    dummy_pdf_path.touch()

    @mistral.ocr
    def process_document_bytes(doc_bytes: bytes):
        """Processes document content provided as bytes."""
        return doc_bytes

    @mistral.ocr
    def process_document_url(url: str):
        """Processes a document located at a public URL."""
        return url

    @mistral.ocr
    def process_document_path(path: str):
        """Processes a document from a local file path."""
        return path

    # Example with Bytes (replace with actual PDF bytes)
    try:
        # pdf_bytes = Path("my_real_document.pdf").read_bytes()
        pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n5 0 obj<</Length 44>>stream\nBT /F1 12 Tf 100 700 Td (Hello, Mirascope!)Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000010 00000 n\n0000000068 00000 n\n0000000128 00000 n\n0000000242 00000 n\n0000000303 00000 n\ntrailer<</Size 6/Root 1 0 R>>\nstartxref\n406\n%%EOF"
        response_bytes = process_document_bytes(pdf_bytes)
        print("OCR from Bytes:")
        print(f"Full Text: {response_bytes.full_text[:100]}...") # Print first 100 chars
        print(f"Pages Processed: {len(response_bytes.pages)}")
    except Exception as e:
        print(f"Error processing bytes (expected with dummy/invalid data): {e}")

    # Example with URL (replace with a real, accessible PDF URL)
    try:
        # Mistral requires a publicly accessible URL
        # Using a known public sample PDF
        pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
        response_url = process_document_url(pdf_url)
        print("\nOCR from URL:")
        print(f"Full Text: {response_url.full_text[:100]}...")
        print(f"Pages Processed: {len(response_url.pages)}")
    except Exception as e:
        print(f"Error processing URL: {e}")

    # Example with Path
    try:
        response_path = process_document_path(str(dummy_pdf_path))
        print("\nOCR from Path (using dummy file):")
        print(f"Full Text: {response_path.full_text[:100]}...")
        print(f"Pages Processed: {len(response_path.pages)}")
    except Exception as e:
        print(f"Error processing path (expected with dummy file): {e}")
    finally:
        # Clean up dummy file
        if dummy_pdf_path.exists():
            dummy_pdf_path.unlink()

    ```

=== "Asynchronous"

    ```python
    import asyncio
    import os
    from pathlib import Path
    from mirascope.core import mistral

    # Ensure MISTRAL_API_KEY is set
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable not set.")

    # Create a dummy PDF file for demonstration
    dummy_pdf_path = Path("dummy_document_async.pdf")
    dummy_pdf_path.touch() # See sync example for notes on dummy data

    @mistral.ocr
    async def process_document_bytes_async(doc_bytes: bytes):
        """Processes document content provided as bytes asynchronously."""
        # In a real async scenario, bytes might be read async, but fn returns them
        return doc_bytes

    @mistral.ocr
    async def process_document_url_async(url: str):
        """Processes a document located at a public URL asynchronously."""
        return url

    @mistral.ocr
    async def process_document_path_async(path: str):
        """Processes a document from a local file path asynchronously."""
        # NOTE: Providing a path string to the async version currently raises
        # NotImplementedError because async file reading isn't built-in.
        # Instead, read the file bytes asynchronously using a library like
        # `aiofiles` and pass the bytes to an async function decorated
        # with `@mistral.ocr` that accepts `bytes`.
        return path

    async def main():
        # Example with Bytes (replace with actual PDF bytes)
        try:
            # pdf_bytes = # Read bytes async if needed
            pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n5 0 obj<</Length 44>>stream\nBT /F1 12 Tf 100 700 Td (Hello, Async Mirascope!)Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000010 00000 n\n0000000068 00000 n\n0000000128 00000 n\n0000000242 00000 n\n0000000303 00000 n\ntrailer<</Size 6/Root 1 0 R>>\nstartxref\n406\n%%EOF"
            response_bytes = await process_document_bytes_async(pdf_bytes)
            print("Async OCR from Bytes:")
            print(f"Full Text: {response_bytes.full_text[:100]}...")
            print(f"Pages Processed: {len(response_bytes.pages)}")
        except Exception as e:
            print(f"Error processing bytes async (expected with dummy/invalid data): {e}")

        # Example with URL (replace with a real, accessible PDF URL)
        try:
            pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
            response_url = await process_document_url_async(pdf_url)
            print("\nAsync OCR from URL:")
            print(f"Full Text: {response_url.full_text[:100]}...")
            print(f"Pages Processed: {len(response_url.pages)}")
        except Exception as e:
            print(f"Error processing URL async: {e}")

        # Example with Path
        try:
            response_path = await process_document_path_async(str(dummy_pdf_path))
            print("\nAsync OCR from Path (using dummy file):")
            print(f"Full Text: {response_path.full_text[:100]}...")
            print(f"Pages Processed: {len(response_path.pages)}")
        except Exception as e:
            print(f"Error processing path async (expected with dummy file): {e}")
        finally:
            # Clean up dummy file
            if dummy_pdf_path.exists():
                dummy_pdf_path.unlink()

    if __name__ == "__main__":
        asyncio.run(main())
    ```

These examples demonstrate how to use the `@mistral.ocr` decorator for different input types in both synchronous and asynchronous contexts. Remember to replace placeholder data (like dummy file paths or URLs) with actual document sources for real-world usage.
