"""Utility for determining the type of an document from its bytes."""


def get_document_type(document_data: bytes) -> str:
    if document_data.startswith(b"%PDF"):
        return "pdf"
    raise ValueError("Unsupported document type")
