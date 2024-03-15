# Extracting base types

Mirascope also makes it possible to extract base types without defining a `pydantic.BaseModel` with the same exact format for extraction:

```python
from mirascope.openai import OpenAIExtractor


class BookRecommender(OpenAIExtractor[list[str]]):
    extract_schema: Type[list[str]] = list[str]
	prompt_template = "Please recommend some science fiction books."


books = BookRecommendation().extract()
print(books)
#> ['Dune', 'Neuromancer', "Ender's Game", "The Hitchhiker's Guide to the Galaxy", 'Foundation', 'Snow Crash']
```

We currently support: `str`, `int`, `float`, `bool`, `list`, `set`, `tuple`, and `Enum`.

We also support using `Union`, `Literal`, and `Annotated` 

!!! note

    If you’re using `mypy` you’ll need to add `#  type: ignore` due to how these types are handled differently by Python.

## Using `Enum` or `Literal` for classification

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
