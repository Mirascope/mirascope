from mirascope import llm


@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


max_retries = 3
for attempt in range(max_retries):
    try:
        response = recommend_book("fantasy")
        print(response.pretty())
        break
    except llm.Error:
        if attempt == max_retries - 1:
            raise
