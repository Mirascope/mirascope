"""Using from_prompt to create an Anthropic call on the fly, using the `Greetings` class.

Note that if you are using multi-line messages in the prompt_template, the providers
need to have the same roles.
"""
import os

from mirascope.anthropic import AnthropicCall, AnthropicCallParams
from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
os.environ["ANTHROPIC_API_KEY"] = "YOUR_ANTHROPIC_API_KEY"


class Greetings(OpenAICall):
    prompt_template = "What is your purpose?"


greetings = AnthropicCall.from_prompt(
    Greetings, AnthropicCallParams(model="claude-3-haiku-20240307")
)

openai_response = Greetings().call()
print(openai_response.content)

anthropic_response = greetings().call()
print(anthropic_response.content)
