"""
Convenience built on top of tools that makes extracting structured information reliable:
"""

import os
from typing import Literal

from pydantic import BaseModel

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


class TaskDetails(BaseModel):
    description: str
    due_date: str
    priority: Literal["low", "normal", "high"]


@openai.call(
    model="gpt-4o",
    stream=True,
    response_model=TaskDetails,
)
def task_extractor(task: str):
    """
    Extract the task details from the following task:
    {task}
    """


task = "Submit quarterly report by next Friday. Task is high priority."
task_details = task_extractor(task=task)
for partial_model in task_details:
    print(partial_model)
# > description='Submit quarterly report' due_date='next Friday' priority='high'
