from enum import Enum
from typing import Any, Optional, Type

from pydantic import BaseModel

from mirascope.groq import GroqCallParams, GroqExtractor


class Priority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class TaskType(BaseModel):
    name: str
    description: str


class TaskDetails(BaseModel):
    title: str
    priority: Priority
    due_date: str
    subtasks: list[str]
    tags: set[str]
    metadata: dict[str, Any]
    related_tasks: tuple[TaskType, ...]
    assignee: Optional[str]


class TaskExtractor(GroqExtractor[TaskDetails]):
    extract_schema: Type[TaskDetails] = TaskDetails

    prompt_template = """
    Please extract the task details from the following description:
    {task}
    """

    task: str

    call_params = GroqCallParams(model="mixtral-8x7b-32768")


task_description = """
Submit the quarterly financial report by next Friday. This task is of high priority.
Subtasks:
- Gather financial data
- Prepare charts and graphs
- Write executive summary

Tags: finance, reporting, Q2
Metadata:
- Department: Accounting
- Fiscal Year: 2023

Related tasks:
- Task 1:
  Name: Review previous quarter's report
  Description: Analyze the previous quarter's financial report for comparison
- Task 2: 
  Name: Schedule board meeting
  Description: Arrange a meeting with the board to present the quarterly report

Assignee: John Doe
"""

task = TaskExtractor(task=task_description).extract(retries=3)
assert isinstance(task, TaskDetails)
print(task.model_dump())
# {
#     "title": "Submit the quarterly financial report",
#     "priority": "<Priority.HIGH: 'high'>",
#     "due_date": "next Friday",
#     "subtasks": [
#         "Gather financial data",
#         "Prepare charts and graphs",
#         "Write executive summary",
#     ],
#     "tags": {"finance", "reporting", "Q2"},
#     "metadata": {"Department": "Accounting", "Fiscal Year": 2023},
#     "related_tasks": (
#         {
#             "name": "Review previous quarter's report",
#             "description": "Analyze the previous quarter's financial report for comparison",
#         },
#         {
#             "name": "Schedule board meeting",
#             "description": "Arrange a meeting with the board to present the quarterly report",
#         },
#     ),
#     "assignee": "John Doe",
# }
