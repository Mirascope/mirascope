from typing import Literal, Type

import logfire
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel

from mirascope.cohere import CohereExtractor
from mirascope.logfire import with_logfire
from mirascope.openai import OpenAIExtractor

logfire.configure()

load_dotenv(find_dotenv())


class TaskDetails(BaseModel):
    description: str
    due_date: str
    priority: Literal["low", "normal", "high"]


@with_logfire
class TaskExtractor(CohereExtractor[TaskDetails]):
    extract_schema: Type[TaskDetails] = TaskDetails
    prompt_template = """
    Extract the task details from the following task:
    {task}
    """

    task: str


task = "Submit quarterly report by next Friday. Task is high priority."
task_details = TaskExtractor(
    task=task
).extract()  # this will be logged automatically with logfire
assert isinstance(task_details, TaskDetails)
print(task_details)
