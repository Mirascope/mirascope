"""Basic example using an @openai.call to extract structured information with Langfuse."""

import os
from typing import Literal

import logfire
from pydantic import BaseModel

from mirascope.core import openai
from mirascope.integrations.langfuse import with_langfuse

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"
logfire.configure()


class TaskDetails(BaseModel):
    description: str
    due_date: str
    priority: Literal["low", "normal", "high"]


@with_langfuse
@openai.call(model="gpt-3.5-turbo", response_model=TaskDetails)
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
