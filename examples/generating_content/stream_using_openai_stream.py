"""
Basic example using an OpenAIStream to stream a call. You get access to properties
like `cost`, `message_param`, and `user_message_param`.
"""

import os

from mirascope.openai import OpenAICall, OpenAIStream

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class BookRecommender(OpenAICall):
    prompt_template = "Please recommend a {genre} book."

    genre: str


stream = BookRecommender(genre="fantasy").stream()
openai_stream = OpenAIStream(stream)
for chunk, tool in openai_stream:
    print(chunk.content, end="")
# > I recommend "The Name of the Wind" by Patrick Rothfuss...

print(openai_stream.cost)
# > 0.0001235
print(openai_stream.message_param)
# > {'role': 'assistant', 'content': 'I recommend "The Name of the Wind" by Patrick Rothfuss...'}
print(openai_stream.user_message_param)
# > {'content': 'Please recommend a fantasy book.', 'role': 'user'}
