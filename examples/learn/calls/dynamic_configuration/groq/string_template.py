from mirascope.core import BaseDynamicConfig, groq, prompt_template


@groq.call("llama-3.1-8b-instant")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> BaseDynamicConfig:
    return {
        "call_params": {"max_tokens": 512},
        "metadata": {"tags": {"version:0001"}},
    }


print(recommend_book("fantasy"))
