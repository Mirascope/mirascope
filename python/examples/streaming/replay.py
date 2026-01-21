from mirascope import llm


@llm.call("openai/gpt-5-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book.stream("fantasy")

# First iteration - consumes from LLM
print("First pass:")
for chunk in response.text_stream():
    print(chunk, end="", flush=True)

# Second iteration - replays from cache
# This will print everything immediately, and is approximately equivalent to calling
# print(stream_response.pretty())
print("Second pass (replay):")
for chunk in response.text_stream():
    print(chunk, end="", flush=True)
