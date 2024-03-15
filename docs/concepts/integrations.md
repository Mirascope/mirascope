# Integrations

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

## Weights & Biases

If you want to seamlessly use Weights & Biases’ logging functionality, we’ve got you covered -  [`WandbOpenAICall`](../api/openai/wandb.md#mirascope.openai.wandb.WandbOpenAICall) is an `OpenAICall` with unique creation methods that internally call W&B’s `Trace()` function and log your runs. For standard chat completions, you can use `WandbOpenAICall.call_with_trace()`, and for extractions, you can use [`WandbOpenAIExtractor`](../api/openai/wandb.md#mirascope.openai.wandb.WandbOpenAIExtractor)'s `extract_with_trace` method.

### Generating Content with a W&B Trace

The `call_with_trace()` function internally calls both `OpenAICall.call()` and `wandb.Trace()` and is configured to properly log both successful completions and errors. 

Note that unlike a standard `OpenAICall`, it requires the argument `type` to specify the type of `Trace` it initializes.  Once called, it will return a tuple of the `OpenAICallResponse`  and the created span `Trace`. 

```python
import os
from mirascope.openai.wandb import WandbPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class Explainer(WandbOpenAICall):
	prompt_template = "Tell me more about {topic} in detail."
	
	topic: str


response, span = Explainer(type="llm",topic="the Roman Empire").call_with_trace()
span.log(name="my_trace")
```

In addition, `call_with_trace` can take an argument  `parent` for chained completions, and the initialized `Trace` will be linked with its parent within W&B logs. 

```python
import os
from mirascope.wandb import WandbPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class Explainer(WandbOpenAICall):
	prompt_template = "Tell me more about {topic} in detail."

	topic: str


class Summarizer(WandbOpenAICall):
	prompt_template = "Summarize the following: {text}"

	text: str


explainer = Explainer(type="llm",topic="the Roman Empire")
response, explain_span = explainer.call_with_trace()

summarizer = Summarizer(type="llm", text=explanation.content)
response, _ = summarizer.call_with_trace(explain_span)

explain_span.log(name="my_trace")
```

Since `WandbOpenAICall` inherits from `OpenAICall`, it will support function calling the same way you would a standard `OpenAICall`, as seen [here](tools_(function_calling).md)

### Extracting with a W&B Trace

When working with longer chains, it is often useful to use extractions so that data is passed along in a structured format. Just like `call_with_trace()` , you will need to pass in a `type` argument to the extractor and a `parent` to the extraction.

```python
import os
from typing import Type

from mirascope.wandb import WandbOpenAIExtractor

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class OceanCounter(WandbOpenAIExtractor[int]):
	extract_schema: Type[int] = int
	prompt_template = "There are 7 oceans on earth."


num_oceans, span = OceanCounter(type="tool").extract_with_trace()

span.log(name="mirascope_trace")
```

## LangChain and LangSmith

### Logging a LangSmith trace

You can use client wrappers (as mentioned in the first section of this doc) to integrate Mirascope with LangSmith. When using a wrapper, you can generate content as you would with a normal `OpenAICall`:

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
