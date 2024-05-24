"""
Colocation is the core of our philosophy. Everything that can impact the quality of a
call to an LLM — from the prompt to the model to the temperature — must live together
so that we can properly version and test the quality of our calls over time. This is
useful since we have all of the information including metadata that we could want for
analysis, which is particularly important during rapid development.
"""

import os

from mirascope import tags
from mirascope.openai import OpenAICall, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


@tags(["version:0003"])
class Editor(OpenAICall):
    prompt_template = """
	SYSTEM:
	You are a top class manga editor.
	
	USER:
	I'm working on a new storyline. What do you think?
	{storyline}
	"""

    storyline: str

    call_params = OpenAICallParams(model="gpt-4", temperature=0.4)


storyline = "..."
editor = Editor(storyline=storyline)

print(editor.messages())
# > [{'role': 'system', 'content': 'You are a top class manga editor.'}, {'role': 'user', 'content': "I'm working on a new storyline. What do you think?\n..."}]

critique = editor.call()
print(critique.content)
# > I think the beginning starts off great, but...

print(editor.dump() | critique.dump())
# {
#     "tags": ["version:0003"],
#     "template": "SYSTEM:\nYou are a top class manga editor.\n\nUSER:\nI'm working on a new storyline. What do you think?\n{storyline}",
#     "inputs": {"storyline": "..."},
#     "start_time": 1710452778501.079,
#     "end_time": 1710452779736.8418,
#     "output": {
#         "id": "chatcmpl-92nBykcXyTpxwAbTEM5BOKp99fVmv",
#         "choices": [
#             {
#                 "finish_reason": "stop",
#                 "index": 0,
#                 "logprobs": None,
#                 "message": {
#                     "content": "As an AI, I need some more context to provide a valuable opinion. Could you please share the details of the storyline?",
#                     "role": "assistant",
#                     "function_call": None,
#                     "tool_calls": None,
#                 },
#             }
#         ],
#         "created": 1710452778,
#         "model": "gpt-4-0613",
#         "object": "chat.completion",
#         "system_fingerprint": None,
#         "usage": {"completion_tokens": 25, "prompt_tokens": 33, "total_tokens": 58},
#     },
# }
