# Streaming Tools and Structured Outputs

When using [tools (function calling)](./tools_(function_calling).md) or [extracting structured information](./extracting_structured_information_using_llms.md), there are many instances in which you will want to stream the results. For example, consider making a call to an LLM that responds with multiple tool calls. Your system can have more real-time behavior if you can call each tool as it's returned instead of having to wait for all of them to be generated at once. Another example would be when returning structured information to a UI. Streaming the information enables real-time generative UI that can be generated as the fields are streamed.

!!! note

    Currently streaming tools is only supported for OpenAI and Anthropic. We will aim to add support for other model providers when available in their APIs.

## Streaming Tools (Function Calling)

To stream tools, first call `stream` instead of `call` for an LLM call with tools. Then use the matching provider's tool stream class to stream the tools:

```python
import os

from mirascope.openai import OpenAICall, OpenAICallParams, OpenAIToolStream

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


def print_book(title: str, author: str, description: str):
    """Prints the title and author of a book."""
    return f"Title: {title}\nAuthor: {author}\nDescription: {description}"


class BookRecommender(OpenAICall):
    prompt_template = "Please recommend some books to read."

    call_params = OpenAICallParams(tools=[print_book])


stream = BookRecommender().stream()
tool_stream = OpenAIToolStream.from_stream(stream)
for tool in tool_stream:
    tool.fn(**tool.args)
#> Title: The Name of the Wind\nAuthor: Patrick Rothfuss\nDescription: ...
#> Title: Dune\nAuthor: Frank Herbert\nDescription: ...
#> ...
```

### Streaming Partial Tools

Sometimes you may want to stream partial tools as well (i.e. the unfinished tool call with `None` for arguments that haven't yet been streamed). This can be useful for example when observing an agent's flow in real-time. You can simple set `allow_partial=True` to access this feature. In the following code example, we stream each partial tool and update a live console, printing each full tool call before moving on to the next:

```python hl_lines="20"
import os
import time

from rich.live import Live

from mirascope.openai import OpenAICall, OpenAICallParams, OpenAIToolStream

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


def print_book(title: str, author: str, description: str):
    """Prints the title and author of a book."""
    return f"Title: {title}\nAuthor: {author}\nDescription: {description}"


class BookRecommender(OpenAICall):
    prompt_template = "Please recommend some books to read."

    call_params = OpenAICallParams(tools=[print_book])


stream = BookRecommender().stream()
tool_stream = OpenAIToolStream.from_stream(stream, allow_partial=True)

with Live("", refresh_per_second=15) as live:
    partial_tools, index = [None], 0
    previous_tool = None
    for partial_tool in tool_stream:
        if partial_tool is None:
            index += 1
            partial_tools.append(None)
            continue
        partial_tools[index] = partial_tool
        live.update(
            "\n-----------------------------\n".join(
                [pt.fn(**pt.args) for pt in partial_tools]
            )
        )
        time.sleep(0.1)
```

## Streaming Pydantic Models

You can also stream structured outputs when using an extractor. Simply call the `stream` function to stream partial outputs:

```python
import os
from typing import Literal, Type

from mirascope.openai import OpenAIExtractor
from pydantic import BaseModel

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class TaskDetails(BaseModel):
    title: str
    priority: Literal["low", "normal", "high"]
    due_date: str


class TaskExtractor(OpenAIExtractor[TaskDetails]):
    extract_schema: Type[TaskDetails] = TaskDetails

    prompt_template = """
    Please extract the task details:
    {task}
    """

    task: str


task_description = "Submit quarterly report by next Friday. Task is high priority."
stream = TaskExtractor(task=task_description).stream()
for partial_model in stream:
    print(partial_model)
#> title='Submit quarterly report' priority=None due_date=None
#> title='Submit quarterly report' priority='high' due_date=None
#> title='Submit quarterly report' priority='high' due_date='next Friday'
```
