# LangChain and LangSmith

## Using Mirascope [`BasePrompt`](../api/base/prompts.md#mirascope.base.prompts.BasePrompt) with LangChain

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

## Logging a LangSmith trace

You can use client wrappers (as mentioned in [client wrappers](./client_wrappers.md)) to integrate Mirascope with LangSmith. When using a wrapper, you can generate content as you would with a normal `OpenAICall`:

```python
import os
from langsmith import wrappers
from mirascope.base import BaseConfig
from mirascope.openai import OpenAICall
os.environ["LANGCHAIN_API_KEY"] = "YOUR_LANGCHAIN_API_KEY"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class BookRecommender(OpenAICall):
    prompt_template = "Can you recommend some books on {topic}?"

    topic: str

    configuration = BaseConfig(client_wrappers[wrappers.wrap_openai])


response = BookRecommender(topic="sci-fi").call()
```

Now, if you log into [LangSmith](https://smith.langchain.com/) , you will be see your results have been traced. Of course, this integration works not just for `call`, but also for `stream` and `extract`.
