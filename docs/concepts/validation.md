# Validation

When extracting structured information from LLMs, it’s important that we validate the extracted information, especially the types. We want to make sure that if we’re looking for an integer that we actual get an `int` back. One of the primary benefits of building on top of [Pydantic](https://pydantic.dev/) is that it makes validation easy — in fact, we get validation on types out-of-the-box.

We recommend you check out their [thorough documentation](https://docs.pydantic.dev/latest/concepts/validators/) for detailed information on everything you can do with their validators. This document will be brief and specifically related to LLM extraction to avoid duplication.

## Validating Types

When we extract information — for base types, `BaseModel`, or any of our tools — everything is powered by Pydantic. This means that we automatically get type validation and can handle it gracefully:

```python
from typing import Type

from mirascope.openai import OpenAIExtractor
from pydantic import BaseModel, ValidationError


class Book(BaseModel):
	title: str
	price: float


class BookRecommender(OpenAIExtractor[Book]):
    extract_schema: Type[Book] = Book
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

## Custom Validation

It’s often useful to write custom validation when working with LLMs so that we can automatically handle things that are difficult to hard-code. For example, consider determining whether the generated content adheres to your company’s guidelines. It’s a difficult task to determine this, but an LLM is well-suited to do the task well.

We can use an LLM to make the determination by adding an [`AfterValidator`](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.AfterValidator) to our extracted output:

```python
from enum import Enum
from typing import Annotated, Type

from mirascope.openai import OpenAIExtractor
from pydantic import AfterValidator, BaseModel, ValidationError


class Label(Enum):
    HAPPY = "happy story"
    SAD = "sad story"


class Sentiment(OpenAIExtractor[Label]):
    extract_schema: Type[Label] = Label
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
    extract_template: Type[HappyStory] = HappyStory
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
