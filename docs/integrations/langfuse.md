# Langfuse

Mirascope provides out-of-the-box integration with [Langfuse](https://langfuse.com/).

## How to use Langfuse with Mirascope

```python
from mirascope.langfuse import with_langfuse
```

`with_langfuse` is a decorator that can be used on all Mirascope classes to automatically log both Mirascope calls and also all our supported LLM providers.

## Examples

### Call

This is a basic call example but will work with all our call functions, `call`, `stream`, `call_async`, `stream_async`.

```python
import os
from mirascope.langfuse import with_langfuse
from mirascope.anthropic import AnthropicCall

os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-..."
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-..."
os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"


@with_langfuse
class BookRecommender(AnthropicCall):
    prompt_template = "Please recommend some {genre} books"

    genre: str


recommender = BookRecommender(genre="fantasy")
response = recommender.call()  # this will automatically get logged with langfuse
print(response.content)
#> Here are some recommendations for great fantasy book series: ...
```

This will give you:

A trace around the AnthropicCall.call() that captures items like the prompt template, and input/output attributes and more.
Human-readable display of the conversation with the agent
Details of the response, including the number of tokens used

## Extract

```python
import os
from mirascope.langfuse import with_langfuse
from mirascope.openai import OpenAIExtractor

os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-..."
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-..."
os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"

class TaskDetails(BaseModel):
    description: str
    due_date: str
    priority: Literal["low", "normal", "high"]


@with_langfuse
class TaskExtractor(OpenAIExtractor[TaskDetails]):
    extract_schema: Type[TaskDetails] = TaskDetails
    prompt_template = """
    Extract the task details from the following task:
    {task}
    """

    task: str


task = "Submit quarterly report by next Friday. Task is high priority."
task_details = TaskExtractor(
    task=task
).extract()  # this will be logged automatically with langfuse
assert isinstance(task_details, TaskDetails)
print(task_details)
# > description='Submit quarterly report' due_date='next Friday' priority='high'
```

This will give you:

Same view as you would get from using `langfuse.openai`. We will be adding more extraction support for other providers soon.
