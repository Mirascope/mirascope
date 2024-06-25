"""
Convenience built on top of tools that makes extracting structured information reliable:
(Gemini)
"""

from typing import Literal

from google.generativeai import configure
from pydantic import BaseModel

from mirascope.core import gemini

configure(api_key="YOUR_GEMINI_API_KEY")


class TaskDetails(BaseModel):
    description: str
    due_date: str
    priority: Literal["low", "normal", "high"]


@gemini.call(model="gemini-1.5-pro", response_model=TaskDetails)
def task_extractor(task: str):
    """
    Extract the task details from the following task:
    {task}
    """


task = "Submit quarterly report by next Friday. Task is high priority."
task_details = task_extractor(task=task)
assert isinstance(task_details, TaskDetails)
print(task_details)
# > description='Submit quarterly report' due_date='next Friday' priority='high'
