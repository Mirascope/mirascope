"""This example shows how to call Ollama with Mirascope.

Set the base_url to the URL of your Ollama instance and set the api_key to ollama.
"""
from mirascope.openai import OpenAICall, OpenAICallParams


class RecipeRecommender(OpenAICall):
    prompt_template = "Recommend recipes that use {ingredient} as an ingredient"

    ingredient: str

    api_key = "ollama"
    base_url = "http://localhost:11434/v1"
    call_params = OpenAICallParams(model="mistral")
