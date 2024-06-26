# Weights & Biases

If you want to seamlessly use Weights & Biases’ logging functionality, we’ve got you covered.

## Weave

Mirascope seamlessly integrates with Weave with just a few lines of code. You can use it with any `BaseCall` or `BaseExtractor` extension such as `OpenAICall` or `AnthropicCall`. Simply add the [`with_weave`](../api/wandb/weave.md#mirascope.wandb.weave.with_weave) decorator to your class and the `call`, `call_async`, `stream`, `stream_async`, `extract`, and `extract_async` methods will be automatically logged to the Weave project you initialize.

The below examples show how to use the `with_weave` decorator to automatically log your runs to Weave. We've highlighted the lines that we've added to the original example to demonstrate how easy it is to use Weave with Mirascope.

### Call Example

```python hl_lines="1 4 6 9"
import weave

from mirascope.openai import OpenAICall
from mirascope.wandb import with_weave

weave.init("my-project")


@with_weave
class BookRecommender(OpenAICall):
	prompt_template = "Please recommend some {genre} books"
	
	genre: str


recommender = BookRecommender(genre="fantasy")
response = recommender.call()  # this will automatically get logged with weave
print(response.content)
```

### Extract Example

```python hl_lines="3 7 9 18"
from typing import Literal, Type

import weave
from pydantic import BaseModel

from mirascope.openai import OpenAIExtractor
from mirascope.wandb import with_weave

weave.init("scratch-test")


class TaskDetails(BaseModel):
    description: str
    due_date: str
    priority: Literal["low", "normal", "high"]


@with_weave
class TaskExtractor(OpenAIExtractor[TaskDetails]):
    extract_schema: Type[TaskDetails] = TaskDetails
    prompt_template = """
	Extract the task details from the following task:
	{task}
	"""

    task: str


task = "Submit quarterly report by next Friday. Task is high priority."
task_details = TaskExtractor(task=task).extract()  # this will be logged automatically
assert isinstance(task_details, TaskDetails)
print(task_details)
```

## Trace

[`WandbCallMixin`](../api/wandb/wandb.md#mirascope.wandb.wandb.WandbCallMixin) is a mixin with creation methods that internally call W&B’s `Trace()` function so you can easily log your runs. For standard responses, you can use `call_with_trace()`, and for extractions, you can use [`WandbExtractorMixin`](../api/wandb/wandb.md#mirascope.wandb.wandb.WandbExtractorMixin)'s `extract_with_trace` method. These mixins are agnostic to the LLM provider, so you can use it with any `BaseCall` or `BaseExtractor` extension such as `OpenAICall` or `AnthropicCall`.

### Generating Content with a W&B Trace

The `call_with_trace()` function internally calls both `call()` and `wandb.Trace()` and is configured to properly log both successful completions and errors.

Note that unlike a standard call, it requires the argument `span_type` to specify the type of `Trace` it initializes.  Once called, it will return a tuple of the call response and the created span `Trace`.

```python
import os
from mirascope.openai import OpenAICall, OpenAICallResponse
from mirascope.wandb import WandbCallMixin
import wandb

wandb.login(key="YOUR_WANDB_API_KEY")
wandb.init(project="wandb_logged_chain")

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class Explainer(OpenAICall, WandbCallMixin[OpenAICallResponse]):
	prompt_template = "Tell me more about {topic} in detail."
	
	topic: str


explainer = Explainer(span_type="llm", topic="the Roman Empire")
response, span = explainer.call_with_trace()
span.log(name="my_trace")
```

In addition, `call_with_trace` can take an argument  `parent` for chained calls, and the initialized `Trace` will be linked with its parent within W&B logs.

```python
import os
from mirascope.openai import OpenAICall, OpenAICallResponse
from mirascope.wandb import WandbCallMixin
import wandb

wandb.login(key="YOUR_WANDB_API_KEY")
wandb.init(project="wandb_logged_chain")

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class Explainer(OpenAICall, WandbCallMixin[OpenAICallResponse]):
	prompt_template = "Tell me more about {topic} in detail."

	topic: str


class Summarizer(OpenAICall, WandbCallMixin[OpenAICallResponse]):
	prompt_template = "Summarize the following: {text}"

	text: str


explainer = Explainer(span_type="llm", topic="the Roman Empire")
response, explain_span = explainer.call_with_trace()

summarizer = Summarizer(span_type="llm", text=explanation.content)
response, _ = summarizer.call_with_trace(explain_span)

explain_span.log(name="my_trace")
```

Since `WandbCallMixin` just adds a method to the call of your choice (e.g. `OpenAICall` as above), it will support function calling the same way you would a standard `OpenAICall`, as seen [here](../concepts/tools_(function_calling).md)

### Extracting with a W&B Trace

When working with longer chains, it is often useful to use extractions so that data is passed along in a structured format. Just like `call_with_trace()` , you will need to pass in a `span_type` argument to the extractor and a `parent` to the extraction.

```python
import os
from typing import Type

from mirascope.openai import OpenAIExtractor
from mirascope.wandb import WandbExtractorMixin
import wandb

wandb.login(key="YOUR_WANDB_API_KEY")
wandb.init(project="wandb_logged_chain")

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class OceanCounter(OpenAIExtractor[int], WandbExtractorMixin[int]):
	extract_schema: Type[int] = int
	prompt_template = "There are 7 oceans on earth."


num_oceans, span = OceanCounter(span_type="tool").extract_with_trace()

span.log(name="mirascope_trace")
```
