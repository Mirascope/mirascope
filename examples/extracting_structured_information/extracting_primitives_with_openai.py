"""An example of how to extract primitive data types using OpenAI."""

import os

from mirascope.openai import OpenAIExtractor

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class TaskExtractor(OpenAIExtractor[str]):
    extract_schema: type[str] = str
    prompt_template = "Please extract the priority from this task: {task}"

    task: str


task = "Submit quarterly report by next Friday. Task is high priority."
priority = TaskExtractor(task=task).extract()
print(priority)
# > high
