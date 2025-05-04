
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

@mistral.ocr()
def process_document_bytes(doc_bytes: bytes):
    """Processes document content provided as bytes."""
    return doc_bytes

@mistral.ocr()
def process_document_url(url: str):
    """Processes a document located at a public URL."""
    return url

@mistral.ocr()
def process_document_path(path: str):
    """Processes a document from a local file path."""
    return path

# Example with Bytes (replace with actual PDF bytes)
try:
    # pdf_bytes = Path("my_real_document.pdf").read_bytes()
    # A minimal valid PDF showing "Hello, Mirascope!"
    pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n5 0 obj<</Length 44>>stream\nBT /F1 12 Tf 100 700 Td (Hello, Mirascope!)Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000010 00000 n\n0000000068 00000 n\n0000000128 00000 n\n0000000242 00000 n\n0000000303 00000 n\ntrailer<</Size 6/Root 1 0 R>>\nstartxref\n406\n%%EOF"
    response_bytes = process_document_bytes(pdf_bytes)
    print("OCR from Bytes:")
    print(f"Full Text: {response_bytes.full_text[:100]}...") # Print first 100 chars
    print(f"Pages Processed: {len(response_bytes.pages)}")
except Exception as e:
    print(f"Error processing bytes: {e}")

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
    # Create a minimal valid PDF file for the path example
    path_pdf_path = Path("path_example.pdf")
    path_pdf_path.write_bytes(pdf_bytes) # Use the same minimal PDF content

    response_path = process_document_path(str(path_pdf_path))
    print("\nOCR from Path:")
    print(f"Full Text: {response_path.full_text[:100]}...")
    print(f"Pages Processed: {len(response_path.pages)}")
except Exception as e:
    print(f"Error processing path: {e}")
finally:
    # Clean up dummy files
    if dummy_pdf_path.exists():
        dummy_pdf_path.unlink()
    if path_pdf_path.exists():
        path_pdf_path.unlink()

