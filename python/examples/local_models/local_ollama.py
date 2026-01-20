# 1. Install Ollama: https://ollama.com/download
# 2. Pull a model: ollama pull deepseek-r1:1.5b
# 3. Run this script

from mirascope import llm


@llm.call("ollama/deepseek-r1:1.5b")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book("fantasy")
print(response.pretty())
