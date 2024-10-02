from mirascope.core import groq


@groq.call("llama-3.1-70b-versatile")
def recommend_book(genre: str) -> groq.GroqDynamicConfig:
    return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


print(recommend_book("fantasy"))
