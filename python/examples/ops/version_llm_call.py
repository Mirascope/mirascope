from mirascope import llm, ops


@ops.version(tags=["production"])
@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str) -> str:
    """Recommend a book based on the given genre."""
    return f"Recommend a {genre} book"


# Access version info before calling
print(f"Hash: {recommend_book.version_info.hash}")
print(f"Version: {recommend_book.version_info.version}")

# Call the function
response = recommend_book("fantasy")
print(response.text())
