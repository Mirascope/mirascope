
import asyncio
import os
from pathlib import Path
from mirascope.core import mistral

# Ensure MISTRAL_API_KEY is set
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY environment variable not set.")

# Create a dummy PDF file for demonstration
dummy_pdf_path_async = Path("dummy_document_async.pdf")
dummy_pdf_path_async.touch()

@mistral.ocr()
async def process_document_bytes_async(doc_bytes: bytes):
    """Processes document content provided as bytes asynchronously."""
    # In a real async scenario, bytes might be read async externally first
    return doc_bytes

@mistral.ocr()
async def process_document_url_async(url: str):
    """Processes a document located at a public URL asynchronously."""
    return url

@mistral.ocr()
async def process_document_path_async(path: str):
    """
    Attempts to process a document from a local file path asynchronously.
    NOTE: Providing a path string to the async version currently raises
    NotImplementedError because async file reading isn't built-in.
    Instead, read the file bytes asynchronously using a library like
    `aiofiles` and pass the bytes to an async function decorated
    with `@mistral.ocr` that accepts `bytes`.
    """
    return path

async def main():
    # Example with Bytes (replace with actual PDF bytes)
    try:
        # pdf_bytes = await read_bytes_async("my_real_document.pdf")
        # A minimal valid PDF showing "Hello, Async Mirascope!"
        pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n5 0 obj<</Length 51>>stream\nBT /F1 12 Tf 100 700 Td (Hello, Async Mirascope!)Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000010 00000 n\n0000000068 00000 n\n0000000128 00000 n\n0000000242 00000 n\n0000000310 00000 n\ntrailer<</Size 6/Root 1 0 R>>\nstartxref\n413\n%%EOF"
        response_bytes = await process_document_bytes_async(pdf_bytes)
        print("Async OCR from Bytes:")
        print(f"Full Text: {response_bytes.full_text[:100]}...")
        print(f"Pages Processed: {len(response_bytes.pages)}")
    except Exception as e:
        print(f"Error processing bytes async: {e}")

    # Example with URL (replace with a real, accessible PDF URL)
    try:
        pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
        response_url = await process_document_url_async(pdf_url)
        print("\nAsync OCR from URL:")
        print(f"Full Text: {response_url.full_text[:100]}...")
        print(f"Pages Processed: {len(response_url.pages)}")
    except Exception as e:
        print(f"Error processing URL async: {e}")

    # Example with Path (expected to raise NotImplementedError)
    try:
        response_path = await process_document_path_async(str(dummy_pdf_path_async))
        print("\nAsync OCR from Path (using dummy file):")
        print(f"Full Text: {response_path.full_text[:100]}...")
        print(f"Pages Processed: {len(response_path.pages)}")
    except NotImplementedError as e:
        print(f"\nAsync OCR from Path Error (expected): {e}")
    except Exception as e:
        print(f"\nUnexpected error processing path async: {e}")
    finally:
        # Clean up dummy file
        if dummy_pdf_path_async.exists():
            dummy_pdf_path_async.unlink()

if __name__ == "__main__":
    asyncio.run(main())

