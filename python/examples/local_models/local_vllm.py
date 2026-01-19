# 1. Install vLLM: uv pip install vllm
# 2. Start the server: vllm serve meta-llama/Llama-3.2-1B-Instruct
# 3. Run this script

from mirascope import llm

llm.register_provider(
    "openai:completions",
    scope="vllm/",
    base_url="http://localhost:8000/v1",
    api_key="vllm",  # required by client but unused
)


@llm.call("vllm/meta-llama/Llama-3.2-1B-Instruct")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book("fantasy")
print(response.pretty())
