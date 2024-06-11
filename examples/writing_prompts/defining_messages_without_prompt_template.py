"""Defining messages array without prompt template -- No Magic

This is an example demonstrating how to define types that aren't text.
This example is to demonstrate the syntax on how to define messages and uses openai as
the example. Refer to the provider's documentation on how to define messages.
"""
# from anthropic.types import MessageParam
# from cohere.types import ChatMessage
# from google.generativeai.types import ContentsType  # type: ignore
# from groq.types.chat import ChatCompletionMessageParam
from openai.types.chat import ChatCompletionMessageParam

from mirascope import BasePrompt


class ImageDetection(BasePrompt):
    def messages(self) -> list[ChatCompletionMessageParam]:
        return [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                        },
                    },
                ],
            },
        ]


prompt = ImageDetection()
print(prompt.messages())
# > [
#       {
#           "role": "user",
#           "content": [
#               {"type": "text", "text": "What's in this image?"},
#               {
#                   "type": "image_url",
#                   "image_url": {
#                       "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
#                   },
#               },
#           ],
#       }
#   ]
print(prompt)
# > ""
print(prompt.dump())
# > {"tags": [], "template": "", "inputs": {}}
