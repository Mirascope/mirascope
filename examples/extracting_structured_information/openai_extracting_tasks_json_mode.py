"""
Convenience built on top of tools that makes extracting structured information reliable:
"""

import os


from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


@openai.call(model="gpt-4o", response_format={"type": "json_object"})
def task_extractor(task: str):
    """
    Extract the task details from the following task to json:
    description: str
    due_date: str
    priority: Literal["low", "normal", "high"]
    {task}
    """


task = "Submit quarterly report by next Friday. Task is high priority."
task_details = task_extractor(task=task)
print(task_details)
# > {
#       "description": "Submit quarterly report",
#       "due_date": "next Friday",
#       "priority": "high",
#   }
