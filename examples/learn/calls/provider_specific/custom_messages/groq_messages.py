from mirascope.core import groq


@groq.call("llama-3.3-70b-versatile")
def recommend_book(genre: str) -> groq.GroqDynamicConfig:
    return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


response: groq.GroqCallResponse = recommend_book("fantasy")
print(response.content)
