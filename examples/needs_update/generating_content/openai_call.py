"""Basic example using an @openai.call to make a call."""

import os

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


@openai.call(model="gpt-4o")
def recommend_book(genre: str):
    """Recommend a {genre} book."""


results = recommend_book(genre="fiction")
print(results.content)
# > Sure! If you enjoy contemporary fiction with rich character development and intricate
#   plots, I would recommend "The Night Circus" by Erin Morgenstern. ...
print(results.cost)
# > 0.001575
print(results.usage)
# > CompletionUsage(completion_tokens=101, prompt_tokens=12, total_tokens=113)
print(results.message_param)
# > {
#       "content": 'Sure! If you enjoy contemporary fiction with rich character development and intricate...',
#       "role": "assistant",
#       "tool_calls": None,
#   }
print(results.user_message_param)
# > {"content": "Recommend a fiction book.", "role": "user"}
