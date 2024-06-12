# Extracting structured information with LLMs

Large Language Models (LLMs) are powerful at generating human-like text, but their outputs are inherently unstructured. Many real-world applications require structured data to function properly, such as extracting due dates, priorities, and task descriptions from user inputs for a task management application, or extracting tabular data from unstructured text sources for data analysis pipelines.

Mirascope provides tools and techniques to address this challenge, allowing you to extract structured information from LLM outputs reliably.

## Challenges in Extracting Structured Information

The key challenges in extracting structured information from LLMs include:

1. **Unstructured Outputs**: LLMs are trained on vast amounts of unstructured text data, causing their outputs to be unstructured as well.
2. **Hallucinations and Inaccuracies**: LLMs can sometimes generate factually incorrect information, complicating the extraction of accurate structured data.

## Defining and Extracting Schemas with Mirascope

Mirascope's extraction functionality is built on top of [Pydantic](https://pydantic.dev/). We will walk through the high-level concepts you need to know to get started extracting structured information with LLMs, but we recommend reading [their docs](https://docs.pydantic.dev/latest/) for more detailed explanations of everything that you can do with Pydantic.

Mirascope offers a convenient `extract` method on extractor classes to extract structured information from LLM outputs. This method leverages tools (function calling) to reliably extract the required structured data.

First, let's take a look at a simple example where we want to extrac task details like due date, priority, and description from a user's natural language input:

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

Let's dive a little deeper into what we're doing here.

### Model

Defining the schema for extraction is done via models, which are classes that inherit from [`pydantic.BaseModel`](https://docs.pydantic.dev/latest/concepts/models/). We can then define an extractor dependent on this schema and use it to extract the schema:

```python
from typing import Type

from mirascope.openai import OpenAIExtractor
from pydantic import BaseModel


class Book(BaseModel):
	title: str
	author: str


class BookExtractor(OpenAIExtractor[Book]):
	extract_schema: Type[Book] = Book
	prompt_template = "The Name of the Wind by Patrick Rothfuss."


book = BookExtractor().extract()
assert isinstance(book, Book)
print(book)
#> title='The Name of the Wind' author='Patrick Rothfuss'
```

You can use tool classes like [`OpenAITool`](../api/openai/tools.md#mirascope.openai.tools.OpenAITool) directly if you want to extract a single tool instead of just a schema (which is useful for calling attached functions).

### Field

You can also use [`pydantic.Fields`](https://docs.pydantic.dev/latest/concepts/fields/) to add additional information for each field in your schema. Again, this information will be included in the prompt, and we can take advantage of that:

```python
from typing import Type

from mirascope.openai import OpenAIPrompt
from pydantic import BaseModel, Field


class Book(BaseModel):
	title: str
	author: str = Field(..., description="Last, First")


class BookExtractor(OpenAIExtractor[Book]):
	extract_schema: Type[Book] = Book
	prompt_template = "The Name of the Wind by Patrick Rothfuss."


book = BookExtractor().extract()
assert isinstance(book, Book)
print(book)
#> title='The Name of the Wind' author='Rothfuss, Patrick'
```

Notice how instead of “Patrick Rothfuss” the extracted author is “Rothfuss, Patrick” as desired.

## Extracting base types

Mirascope also makes it possible to extract base types without defining a `pydantic.BaseModel` with the same exact format for extraction:

```python
from mirascope.openai import OpenAIExtractor


class BookRecommender(OpenAIExtractor[list]):
    extract_schema: type[list] = list[str]
    prompt_template = "Please recommend some science fiction books."


books = BookRecommender().extract()
print(books)
#> ['Dune', 'Neuromancer', "Ender's Game", "The Hitchhiker's Guide to the Galaxy", 'Foundation', 'Snow Crash']
```

We currently support: `str`, `int`, `float`, `bool`, `list`, `set`, `tuple`, and `Enum`.

We also support using `Union`, `Literal`, and `Annotated` 

!!! note

    If you’re using `mypy` you’ll need to add `#  type: ignore` due to how these types are handled differently by Python.

### Using `Enum` or `Literal` for classification

One nice feature of extracting base types is that we can easily use `Enum` or `Literal` to define a set of labels that the model should use to classify the prompt. For example, let’s classify whether or not some email text is spam:

```python
from enum import Enum
# from typing import Literal

from mirascope.openai import OpenAIExtractor

# Label = Literal["is spam", "is not spam"]


class Label(Enum):
    NOT_SPAM = "not_spam"
    SPAM = "spam"


class NotSpam(OpenAIExtractor[Label]):
    extract_schema: Type[Label] = Label
    prompt_template = "Your car insurance payment has been processed. Thank you for your business."


class Spam(OpenAIExtractor[Label]):
    extract_schema: Type[Label] = Label
    prompt_template = "I can make you $1000 in just an hour. Interested?"


# assert NotSpam().extract() == "is not spam"
# assert Spam().extract() == "is spam"
assert NotSpam().extract() == Label.NOT_SPAM
assert Spam().extract() == Label.SPAM
```

## Validation

When extracting structured information from LLMs, it’s important that we validate the extracted information, especially the types. We want to make sure that if we’re looking for an integer that we actual get an `int` back. One of the primary benefits of building on top of [Pydantic](https://pydantic.dev/) is that it makes validation easy — in fact, we get validation on types out-of-the-box.

We recommend you check out their [thorough documentation](https://docs.pydantic.dev/latest/concepts/validators/) for detailed information on everything you can do with their validators. This document will be brief and specifically related to LLM extraction to avoid duplication.

### Validating Types

When we extract information — for base types, `BaseModel`, or any of our tools — everything is powered by Pydantic. This means that we automatically get type validation and can handle it gracefully:

```python

from mirascope.openai import OpenAIExtractor
from pydantic import BaseModel, ValidationError


class Book(BaseModel):
	title: str
	price: float


class BookRecommender(OpenAIExtractor[Book]):
    extract_schema: type[Book] = Book
	prompt_template = "Please recommend a book."


try:
	book = BookRecommender().extract()
    assert isinstance(book, Book)
	print(book)
	#> title='The Alchemist' price=12.99
except ValidationError as e:
	print(e)
  #> 1 validation error for Book
  #  price
  #    Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='standard', input_type=str]
  #      For further information visit https://errors.pydantic.dev/2.6/v/float_parsing
```

Now we can proceed with our extracted information knowing that it will behave as the expected type.

### Custom Validation

It’s often useful to write custom validation when working with LLMs so that we can automatically handle things that are difficult to hard-code. For example, consider determining whether the generated content adheres to your company’s guidelines. It’s a difficult task to determine this, but an LLM is well-suited to do the task well.

We can use an LLM to make the determination by adding an [`AfterValidator`](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.AfterValidator) to our extracted output:

```python
from enum import Enum
from typing import Annotated

from mirascope.openai import OpenAIExtractor
from pydantic import AfterValidator, BaseModel, ValidationError


class Label(Enum):
    HAPPY = "happy story"
    SAD = "sad story"


class Sentiment(OpenAIExtractor[Label]):
    extract_schema: type[Label] = Label
    prompt_template = "Is the following happy or sad? {text}."

    text: str


def validate_happy(story: str) -> str:
    """Check if the content follows the guidelines."""
    label = Sentiment(text=story).extract()
    assert label == Label.HAPPY, "Story wasn't happy."
    return story


class HappyStory(BaseModel):
    story: Annotated[str, AfterValidator(validate_happy)]


class StoryTeller(OpenAIExtractor[HappyStory]):
    extract_schema: type[HappyStory] = HappyStory
    prompt_template = "Please tell me a story that's really sad."


try:
    story = StoryTeller().extract()
except ValidationError as e:
    print(e)
    # > 1 validation error for HappyStoryTool
    #   story
    #     Assertion failed, Story wasn't happy. [type=assertion_error, input_value="Once upon a time, there ...er every waking moment.", input_type=str]
    #       For further information visit https://errors.pydantic.dev/2.6/v/assertion_error

```

## Streaming Tools and Structured Outputs

When using [tools (function calling)](./tools_(function_calling).md) or [extracting structured information](./extracting_structured_information_using_llms.md), there are many instances in which you will want to stream the results. For example, consider making a call to an LLM that responds with multiple tool calls. Your system can have more real-time behavior if you can call each tool as it's returned instead of having to wait for all of them to be generated at once. Another example would be when returning structured information to a UI. Streaming the information enables real-time generative UI that can be generated as the fields are streamed.

!!! note

    Currently streaming tools is only supported for OpenAI and Anthropic. We will aim to add support for other model providers when available in their APIs.

### Streaming Tools (Function Calling)

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

#### Streaming Partial Tools

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

### Streaming Pydantic Models

You can also stream structured outputs when using an extractor. Simply call the `stream` function to stream partial outputs:

```python
import os
from typing import Literal

from mirascope.openai import OpenAIExtractor
from pydantic import BaseModel

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class TaskDetails(BaseModel):
    title: str
    priority: Literal["low", "normal", "high"]
    due_date: str


class TaskExtractor(OpenAIExtractor[TaskDetails]):
    extract_schema: type[TaskDetails] = TaskDetails

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

## Generating Synthetic Data

In the above examples, we’re extracting information present in the prompt text into structured form. We can also use `extract` to generate structured information from a prompt:

```python hl_lines="6"
from mirascope.openai import OpenAIPrompt
from pydantic import BaseModel


class Book(BaseModel):
	"""A science fiction book."""

	title: str
	author: str


class BookRecommender(OpenAIPrompt[Book]):
	extract_schema: type[Book] = Book
	prompt_template = "Please recommend a book."

book = BookRecommender().extract()
assert isinstance(book, Book)
print(book)
#> title='Dune' author='Frank Herbert'
```

Notice that the docstring for the `Book` schema specified a science fiction book, which resulted in the model recommending a science fiction book. The docstring gets included with the prompt as part of the schema definition, and you can use this to your advantage for better prompting.
