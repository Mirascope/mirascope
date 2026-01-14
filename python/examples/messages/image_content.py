from mirascope import llm

# Image from URL (provider downloads directly)
image_url = llm.Image.from_url("https://example.com/photo.jpg")

# Image from local file (base64 encoded)
image_file = llm.Image.from_file("photo.jpg")

# Image from raw bytes
image_bytes = llm.Image.from_bytes(b"...")

# Include image in a message
message = llm.messages.user(["What's in this image?", image_url])
