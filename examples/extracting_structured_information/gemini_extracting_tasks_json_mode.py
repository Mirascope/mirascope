"""Extracting unstructured information into json using json mode for Gemini:"""


from google.generativeai import configure

from mirascope.core import gemini

configure(api_key="YOUR_GEMINI_API_KEY")


@gemini.call(
    model="gemini-1.5-pro",
    generation_config={"response_mime_type": "application/json"},
)
def task_extractor(task: str):
    """
    Extract the task details from the following task:

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
