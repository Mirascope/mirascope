# Defining and extracting schemas

Mirascope is built on top of [Pydantic](https://pydantic.dev/). We will walk through the high-level concepts you need to know to get started extracting structured information with LLMs. We recommend reading [their docs](https://docs.pydantic.dev/latest/) for more detailed explanations of everything that you can do with Pydantic.

## Model

Defining the schema for extraction is done via models, which are classes that inherit from [`pydantic.BaseModel`](https://docs.pydantic.dev/latest/concepts/models/). We can then use a prompt to extract this schema:

```python
from mirascope.openai import OpenAIPrompt
from pydantic import BaseModel


class Book(BaseModel):
	title: str
	author: str


class BookRecommendation(OpenAIPrompt):
	"""The Name of the Wind by Patrick Rothfuss."""


book = BookRecommendation().extract(Book)
print(book)
#> title='The Name of the Wind' author='Patrick Rothfuss'
```

You can use tool classes like [`OpenAITool`](../api/openai/tools.md#mirascope.openai.tools.OpenAITool) directly if you want to extract a single tool instead of just a schema (which is useful for calling attached functions).

## Field

You can also use [`pydantic.Fields`](https://docs.pydantic.dev/latest/concepts/fields/) to add additional information for each field in your schema. Again, this information will be included in the prompt, and we can take advantage of that:

```python
from mirascope.openai import OpenAIPrompt
from pydantic import BaseModel, Field


class Book(BaseModel):
	title: str
	author: str = Field(..., description="Last, First")


class BookRecommendation(OpenAIPrompt):
	"""The Name of the Wind by Patrick Rothfuss."""


book = BookRecommendation().extract(Book)
print(book)
#> title='The Name of the Wind' author='Rothfuss, Patrick'
```

Notice how instead of “Patrick Rothfuss” the extracted author is “Rothfuss, Patrick” as desired.

## Retries

Sometimes the model will fail to extract the schema. This can often be a result of the prompt; however, sometimes it’s simply a failure of the model. If you want to retry the extraction some number of times, you can set `retries` equal to however many retries you want to run (defaults to 0).

```python
book = BookRecommendation().extract(Book, retries=3)  # will retry up to 3 times 
```

## Generating Synthetic Data

In the above examples, we’re extracting information present in the prompt text into structured form. We can also use `extract` to generate structured information from a prompt:

```python
from mirascope.openai import OpenAIPrompt
from pydantic import BaseModel


class Book(BaseModel):
	"""A fantasy book."""

	title: str
	author: str


class BookRecommendation(OpenAIPrompt):
	"""Please recommend a book."""

book = BookRecommendation().extract(Book)
print(book)
#> title='Dune' author='Frank Herbert'
```

Notice that the docstring for the `Book` schema specified a science fiction book, which resulted in the model recommending a science fiction book. The docstring gets included with the prompt as part of the schema definition, and you can use this to your advantage for better prompting.
