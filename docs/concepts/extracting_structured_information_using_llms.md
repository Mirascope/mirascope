# Extracting structured information with LLMs

Large Language Models (LLMs) are powerful at generating human-like text, but their outputs are inherently unstructured. Many real-world applications require structured data to function properly, such as extracting due dates, priorities, and task descriptions from user inputs for a task management application, or extracting tabular data from unstructured text sources for data analysis pipelines.

Mirascope provides tools and techniques to address this challenge, allowing you to extract structured information from LLM outputs reliably.

## Challenges in Extracting Structured Information

The key challenges in extracting structured information from LLMs include:

1. **Unstructured Outputs**: LLMs are trained on vast amounts of unstructured text data, causing their outputs to be unstructured as well.
2. **Hallucinations and Inaccuracies**: LLMs can sometimes generate factually incorrect information, complicating the extraction of accurate structured data.

## Mirascope's Approach

Mirascope offers a convenient `extract` method on extractor classes to extract structured information from LLM outputs. This method leverages tools (function calling) to reliably extract the required structured data. While you can find more details in the following pages, let's consider a simple example where we want to extract task details like due date, priority, and description from a user's natural language input:

```python
from typing import Literal

from mirascope.openai import OpenAIExtractor
from pydantic import BaseModel


class TaskDetails(BaseModel):
    due_date: str
    priority: Literal["low", "normal", "high"]
    description: str


class TaskExtractor(OpenAIExtractor[TaskDetails]):
    extract_schema: Type[TaskDetails] = TaskDetails
    prompt_template = """
    Extract the task details from the following task:
    {task}
    """

    task: str


task = "Submit quarterly report by next Friday. Task is high priority."
task_details = TaskExtractor(task=task).extract()
assert isinstance(task_details, TaskDetails)
print(TaskDetails)
#> due_date='next Friday' priority='high' description='Submit quarterly report'
```

### Retry

Extraction can fail due to a wide variety of reasons. When this happens, the simpliest approach is to introduce retries. Mirascope uses [Tenacity](https://tenacity.readthedocs.io/en/latest/) so that you can customize the behavior of retries or pass in an integer. With the same example above add:

```python
from tenacity import Retrying, stop_after_attempt

retries = Retrying(
    stop=stop_after_attempt(3),
)
task_details = TaskExtractor(task=task).extract(retries=retries)
```

As you can see, Mirascope makes extraction extremely simple. Under the hood, Mirascope uses the provided schema to extract the generated content and validate it (see [Validation](validation.md) for more details).
