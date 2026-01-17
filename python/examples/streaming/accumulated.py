from mirascope import llm


@llm.call("openai/gpt-5-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book.stream("fantasy")

# Stream and display content
for chunk in response.text_stream():
    print(chunk, end="", flush=True)

# After streaming, access accumulated content like a regular Response
print(f"\nTexts: {len(response.texts)}")
print(f"Content parts: {len(response.content)}")
print(f"Messages in history: {len(response.messages)}")
print(f"Usage: {response.usage}")
