from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book"


response: llm.SimpleResponse = recommend_book("fantasy")
print(response.text)
# "Here are a few highly recommended fantasy books..."

scifi_response: llm.SimpleResponse = recommend_book("scifi")
print(scifi_response.text)
# ""Here are a few standout science-fiction picks..."