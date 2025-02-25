from mirascope.core import openai


@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
    return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


response: openai.OpenAICallResponse = recommend_book("fantasy")
print(response.content)
