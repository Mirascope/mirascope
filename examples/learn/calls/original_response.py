from mirascope.core import openai


@openai.call(model="gpt-4o-mini")
def recommend_book(genre: str):
    """Recommend a {genre} book."""


recommendation = recommend_book("fantasy")
# `recommendation` is properly typed as `OpenAICallResponse`
print(f"Content: {recommendation.content}")
# `recommendation.response` is properly typed as `ChatCompletion`
print(f"Original Response: {recommendation.response}")
