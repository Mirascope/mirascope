from mirascope import llm

# Document from URL (provider downloads directly)
doc_url = llm.Document.from_url("https://example.com/report.pdf")

# Document from local file (type inferred from extension)
doc_file = llm.Document.from_file("report.pdf")

# Document from raw bytes
doc_bytes = llm.Document.from_bytes(b"...", mime_type="application/pdf")

# Include document in a message
message = llm.messages.user(["Summarize this document:", doc_url])
