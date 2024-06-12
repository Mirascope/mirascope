"""
Extracting structured information with tenacity.Retrying
"""
import os
from typing import Literal, Type

from pydantic import BaseModel, ValidationError
from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from mirascope.openai import OpenAIExtractor

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

retries = Retrying(
    before=lambda x: print(x),
    after=lambda x: print(x),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(ValidationError),
)


class TaskDetails(BaseModel):
    description: str
    due_date: str
    priority: Literal["low", "normal", "high"]


class TaskExtractor(OpenAIExtractor[TaskDetails]):
    extract_schema: Type[TaskDetails] = TaskDetails
    prompt_template = """
	Extract the task details from the following task:
	{task}
	"""

    task: str


task = "Submit quarterly report by next Friday. Task is high priority."
task_details = TaskExtractor(task=task).extract(retries=retries)
assert isinstance(task_details, TaskDetails)
print(task_details)
# > description='Submit quarterly report' due_date='next Friday' priority='high'
