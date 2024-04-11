# Integrations

## Weights & Biases

If you want to seamlessly use Weights & Biases’ logging functionality, we’ve got you covered

### Weave

Mirascope seamlessly integrates with Weave with just a few lines of code. You can use it with any `BaseCall` or `BaseExtractor` extension such as `OpenAICall` or `AnthropicCall`. Simply add the [`with_weave`](../api/wandb/weave.md#mirascope.wandb.weave.with_weave) decorator to your class and the `call`, `call_async`, `stream`, `stream_async`, `extract`, and `extract_async` methods will be automatically logged to the Weave project you initialize.

The below examples show how to use the `with_weave` decorator to automatically log your runs to Weave. We've highlighted the lines that we've added to the original example to demonstrate how easy it is to use Weave with Mirascope.

#### Call Example

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

#### Extract Example

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

### Trace

[`WandbCallMixin`](../api/wandb/wandb.md#mirascope.wandb.wandb.WandbCallMixin) is a mixin with creation methods that internally call W&B’s `Trace()` function so you can easily log your runs. For standard responses, you can use `call_with_trace()`, and for extractions, you can use [`WandbExtractorMixin`](../api/wandb/wandb.md#mirascope.wandb.wandb.WandbExtractorMixin)'s `extract_with_trace` method. These mixins are agnostic to the LLM provider, so you can use it with any `BaseCall` or `BaseExtractor` extension such as `OpenAICall` or `AnthropicCall`.

#### Generating Content with a W&B Trace

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

Since `WandbCallMixin` just adds a method to the call of your choice (e.g. `OpenAICall` as above), it will support function calling the same way you would a standard `OpenAICall`, as seen [here](tools_(function_calling).md)

#### Extracting with a W&B Trace

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

## Client Wrappers

If you want to use Mirascope in conjunction with another library which implements an OpenAI wrapper (such as LangSmith), you can do so easily by setting the `wrapper` parameter within `OpenAICallParams`. Setting this parameter will internally wrap the `OpenAI` client within an `OpenAICall`, giving you access to both sets of functionalities.

```python
from some_library import some_wrapper
from mirascope.openai import OpenAICall


class BookRecommender(OpenAICall):
    prompt_template = "Can you recommend some books on {topic}?"

    topic: str

    call_params = OpenAICallParams(
		model="gpt-3.5-turbo",
		wrapper=some_wrapper
	)
```

Now, every call to `call`, `call_async`, `stream`, and `stream_async` will be executed on top of the wrapped `OpenAI` client.

## LangChain and LangSmith

### Logging a LangSmith trace

You can use client wrappers (as mentioned in the previous section) to integrate Mirascope with LangSmith. When using a wrapper, you can generate content as you would with a normal `OpenAICall`:

```python
import os
from langsmith import wrappers

from mirascope.openai import OpenAICall

os.environ["LANGCHAIN_API_KEY"] = "YOUR_LANGCHAIN_API_KEY"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class BookRecommender(OpenAICall):
    prompt_template = "Can you recommend some books on {topic}?"

    topic: str

    call_params = OpenAICallParams(
	    model="gpt-3.5-turbo",
		wrapper=wrappers.wrap_openai
	)

response = BookRecommender(topic="sci-fi").call()
```

Now, if you log into [LangSmith](https://smith.langchain.com/) , you will be see your results have been traced. Of course, this integration works not just for `call`, but also for `stream` and `extract`.

### Using Mirascope [`BasePrompt`](../api/base/prompts.md#mirascope.base.prompts.BasePrompt) with LangChain

You may also want to use LangChain given it’s tight integration with LangSmith. For us, one issue we had when we first started using LangChain was that their `invoke` function had no type-safety or lint help. This means that calling `invoke({"foox": "foo"})` was a difficult bug to catch. There’s so much functionality in LangChain, and we wanted to make using it more pleasant.

With Mirascope prompts, you can instantiate a `ChatPromptTemplate` from a Mirascope prompt template, and you can use the prompt’s `model_dump` method so you don’t have to worry about the invocation dictionary:

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from mirascope import BasePrompt

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class JokePrompt(BasePrompt):
    prompt_template = "Tell me a short joke about {topic}"

    topic: str


joke_prompt = JokePrompt(topic="ice cream")
prompt = ChatPromptTemplate.from_template(joke_prompt.template())
# ^ instead of:
# prompt = ChatPromptTemplate.from_template("tell me a short joke about {topic}")

model = ChatOpenAI(model="gpt-4")
output_parser = StrOutputParser()
chain = prompt | model | output_parser

joke = chain.invoke(joke_prompt.model_dump())
# ^ instead of:
# joke = chain.invoke({"topic": "ice cream"})
print(joke)
```

## Want more integrations?

If there are features you’d like that we haven’t yet implemented, please submit a feature request to our [GitHub Issues](https://github.com/Mirascope/mirascope/issues).

We also welcome and greatly appreciate [contributions](../CONTRIBUTING.md) if you’re interested in [helping us out](../HELP.md)!
