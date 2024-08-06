"""Extracting unstructured information into primitives using OpenAI:"""

import os

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


@openai.call(
    model="gpt-3.5-turbo",
    response_model=list[str],
)
def task_extractor(task: str):
    """
    Extract the due dates from the following tasks:

    {task}
    """


task = "Submit quarterly report by 2024-03-01. Task is high priority. Submit annual report by 2024-12-31."
task_details = task_extractor(task=task)
assert isinstance(task_details, list)
print(task_details)
print(task_details._response)  # type: ignore
