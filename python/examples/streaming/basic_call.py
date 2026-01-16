from mirascope import llm


@llm.call("openai/gpt-5-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response: llm.StreamResponse = recommend_book.stream("fantasy")
for chunk in response.text_stream():
    print(chunk, end="", flush=True)
