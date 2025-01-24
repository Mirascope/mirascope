from mirascope.core import BaseDynamicConfig, google, prompt_template


@google.call("gemini-1.5-flash")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> BaseDynamicConfig:
    return {
        "call_params": {"max_tokens": 512},
        "metadata": {"tags": {"version:0001"}},
    }


response = recommend_book("fantasy")
print(response.content)
