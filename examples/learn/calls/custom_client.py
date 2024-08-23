from openai import OpenAI

from mirascope.core import openai, prompt_template

# Create a custom OpenAI client
custom_client = OpenAI(
    api_key="your-api-key",
    organization="your-organization-id",
    base_url="https://your-custom-endpoint.com/v1",
)


@openai.call(model="gpt-4o-mini", client=custom_client)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)
