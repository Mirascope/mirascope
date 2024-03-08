# Integrations

## Client Wrappers

If you want to use Mirascope in conjunction with another library which implements an OpenAI wrapper (such as LangSmith), you can do so easily by setting the `wrapper` parameter within `OpenAICallParams`. Setting this parameter will internally wrap the `OpenAI` client within an `OpenAIPrompt`, giving you access to both sets of functionalities.

```python
from some_library import some_wrapper

class BookRecommendationPrompt(BasePrompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str

    call_params = OpenAICallParams(
		model="gpt-3.5-turbo",
		wrapper=some_wrapper
	)
```

Now, every call to `create()`, `async_create()`, `stream()`, and `async_stream()` will be executed on top of the wrapped `OpenAI` client.

## Weights & Biases

If you want to seamlessly use Weights & Biases’ logging functionality, we’ve got you covered -  [`WandbPrompt`](../api/wandb/prompt.md#mirascope.wandb.prompt.WandbPrompt) is an `OpenAIPrompt` with unique creation methods that internally call W&B’s `Trace()` function and log your runs. For standard chat completions, you can use `WandbPrompt.create_with_trace()`, and for extractions, you can use `WandbPrompt.extract_with_trace()`.

### Generating Content with a W&B Trace

The `create_with_trace()` function internally calls both `OpenAIPrompt.create()` and `wandb.Trace()` and is configured to properly log both successful completions and errors. 

Note that unlike a standard `OpenAIPrompt`, it requires the argument `type` to specify the type of `Trace` it initializes.  Once called, it will return a tuple of the `OpenAIChatCompletion`  and the created `Trace`. 

```python
import os
from mirascope.wandb import WandbPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class ExplainPrompt(WandbPrompt):
	"""Tell me more about {topic} in detail."""
	topic: str


prompt = ExplainPrompt(type="llm",topic="the Roman Empire")
completion, span = prompt.create_with_trace()

span.log(name="my_trace")
```

In addition, `create_with_trace` can take an argument  `parent` for chained completions, and the initialized `Trace` will be linked with its parent within W&B logs. 

```python
import os
from mirascope.wandb import WandbPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class ExplainPrompt(WandbPrompt):
	"""Tell me more about {topic} in detail."""
	topic: str


class SummaryPrompt(WandbPrompt):
	"""Summarize the following: {text}"""
	text: str


explain_prompt = ExplainPrompt(type="llm",topic="the Roman Empire")
explanation, explain_span = explain_prompt.create_with_trace()

summary_prompt = SummaryPrompt(type="llm", text=explanation)
summary, summary_span = summary_prompt.create_with_trace(explain_span)

explain_span.log(name="my_trace")
```

Since `WandbPrompt` inherits from `OpenAIPrompt`, it will support function calling the same way you would a standard `OpenAIPrompt`, as seen [here](tools_(function_calling).md)

### Extracting with a W&B Trace

When working with longer chains, it is often useful to use extractions so that data is passed along in a structured format. Just like `create_with_trace()` , you will need to pass in a `type` argument to the prompt and a `parent` to the extraction.

```python
import os
from mirascope.wandb import WandbPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class InfoPrompt(WandbPrompt):
	"""There are 7 oceans on earth."""


info_prompt = InfoPrompt(type="tool")
completion, span = info_prompt.extract_with_trace(
	schema=int,
	parent=root,
)

root_span.log(name="mirascope_trace")
```

To see `WandbPrompt` in further action, feel free to check out the cookbook example [here](../cookbook/wandb_chain.md).

## LangChain and LangSmith

### Logging a LangSmith trace

You can use client wrappers (as mentioned in the first section of this doc) to integrate Mirascope with LangSmith. When using a wrapper, you can generate content as you would with a normal `OpenAIPrompt`:

```python
import os
from langsmith import wrappers

from mirascope.openai import OpenAIPrompt

os.environ["LANGCHAIN_API_KEY"] = "YOUR_LANGCHAIN_API_KEY"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class BookRecommendationPrompt(OpenAIPrompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str

    call_params = OpenAICallParams(
	    model="gpt-3.5-turbo",
		wrapper=wrappers.wrap_openai
	)

completion = BookRecommendationPrompt(topic="sci-fi").create()
```

Now, if you log into [LangSmith](https://smith.langchain.com/) , you will be see your results have been traced. Of course, this integration works not just for `create()`, but also for `stream()` and `extract()`. For more details, check out the cookbook example [here](../cookbook/langsmith.md).

### Using Mirascope prompts with LangChain

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
    """
    tell me a short joke about {topic}
    """

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
