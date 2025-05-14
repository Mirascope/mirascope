# Structured Outputs

Large Language Models (LLMs) generate unstructured text data by default. Structured outputs are essential for building reliable and efficient AI applications, and this notebook demonstrates various techniques for structuring LLM outputs using Mirascope.

These methods help ensure consistency, type safety, and easier integration of LLM responses into your application. For more detailed information on structured outputs in Mirascope, refer to the [Response Models](../../../learn/response_models) documentation, [JSON Mode](../../../learn/json_mode) documentation, and [Output Parser](../../../learn/output_parsers) documentation.

## Setup

First, let's set up our environment by installing Mirascope and importing the necessary modules.


```python
!pip install "mirascope[openai]"
```


```python
import os

# Set your API keys
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"
```

## Extracting Structured Outputs

The simplest way to extract structured outputs with Mirascope is using `response_model` to define the output type of the call:


```python
from mirascope.core import openai
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


@openai.call("gpt-4o-mini", response_model=Book)
def extract_book(text: str) -> str:
    return f"Extract the book from this text: {text}"


book = extract_book("The Name of the Wind by Patrick Rothfuss")
assert isinstance(book, Book)
print(book)
```

    title='The Name of the Wind' author='Patrick Rothfuss'


In this example we are:
1. Defining a response model `Book` as a Pydantic `BaseModel` subclass
2. Setting `response_model` equal to our `Book` type.
3. Running our LLM API call function as normal, except the output is now a `Book` instance.

## Generating Structured Outputs

Another common use-case for structured outputs is to generate synthetic data. The interface is the same, requiring only an update to the prompt:


```python
@openai.call("gpt-4o-mini", response_model=list[Book])
def recommend_books(genre: str, num: int) -> str:
    return f"Recommend a list of {num} {genre} books"


books = recommend_books("fantasy", 3)
for book in books:
    print(book)
```

    title='The Name of the Wind' author='Patrick Rothfuss'
    title='Mistborn: The Final Empire' author='Brandon Sanderson'
    title='A Darker Shade of Magic' author='V.E. Schwab'


In this example we:
1. Updated our prompt to instruct to model to "recommend" (i.e. generate) books.
2. We set `response_model` equal to `list[Book]` to output multiple books instead of just one.
3. We further updated our prompt to enable the user to specify how many books to generate.

## JSON Mode

Many LLM providers have JSON Mode to instruct the model to output JSON. Although not all providers offer JSON Mode support officially, Mirascope offers support for all providers. For providers with official support, we simply use the native API feature. For providers without official support, we prompt engineer the model to give us the JSON:


```python
import json


@openai.call("gpt-4o-mini", json_mode=True)
def extract_book(text: str) -> str:
    return f"Extract the book title and author from this text: {text}"


response = extract_book("The Name of the Wind by Patrick Rothfuss")
print(json.loads(response.content))
```

    {'title': 'The Name of the Wind', 'author': 'Patrick Rothfuss'}


In this example we:
1. Set `json_mode=True` to signal we want to use JSON Mode
2. Specify the fields that we want in the prompt
3. Parse the json string output into a Python dictionary

If you want additional validation on the output structure and types, you can use `json_mode` in conjunction with `response_model` to validate your structured outputs:




```python
@openai.call("gpt-4o-mini", response_model=Book, json_mode=True)
def extract_book(text: str) -> str:
    return f"Extract the book from this text: {text}"


book = extract_book("The Name of the Wind by Patrick Rothfuss")
assert isinstance(book, Book)
print(book)
```

    title='The Name of the Wind' author='Patrick Rothfuss'


## Few-Shot Examples

Often when guiding an LLM's response, providing few-shot examples can greatly help steer the output in the right direction:


```python
from pydantic import ConfigDict, Field


class FewShotBook(BaseModel):
    title: str = Field(..., examples=["THE NAME OF THE WIND"])
    author: str = Field(..., examples=["Rothfuss, Patrick"])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"},
            ]
        }
    )


@openai.call("gpt-4o-mini", response_model=list[FewShotBook], json_mode=True)
def recommend_few_shot_books(genre: str, num: int) -> str:
    return f"Recommend a list of {num} {genre} books. Match example format."


books = recommend_few_shot_books("fantasy", 3)
for book in books:
    print(book)
```

    title='THE HOBBIT' author='Tolkien, J.R.R.'
    title='A WIZARD OF EARTHSEA' author='Le Guin, Ursula K.'
    title='A GAME OF THRONES' author='Martin, George R.R.'


In this example we:
1. Added a few-shot example to each field in our response model.
2. Added a few-shot example for the entire response model.
3. Set `json_mode=True` because we have found that examples are more effective with this setting.
4. Updated the prompt to instruct the LLM to match the format of the examples.

## Validating Outputs

Since `response_model` relies on Pydantic `BaseModel` types, you can easily add additional validation criteria to your model. This ensures the validation will run on every call:


```python
from pydantic import field_validator


class ValidatedBook(BaseModel):
    title: str
    author: str

    @field_validator("title", "author")
    @classmethod
    def must_be_uppercase(cls, v: str) -> str:
        assert v.isupper(), "All fields must be uppercase"
        return v


@openai.call("gpt-4o-mini", response_model=ValidatedBook)
def extract_all_caps_book(text: str) -> str:
    return f"Extract the book from this text: {text}"


book = extract_all_caps_book("The Name of the Wind by Patrick Rothfuss")
print(book)
```


    ---------------------------------------------------------------------------

    ValidationError                           Traceback (most recent call last)

    Cell In[7], line 20
         15 @openai.call("gpt-4o-mini", response_model=ValidatedBook)
         16 def extract_all_caps_book(text: str) -> str:
         17     return f"Extract the book from this text: {text}"
    ---> 20 book = extract_all_caps_book("The Name of the Wind by Patrick Rothfuss")
         21 print(book)


    File ~/Mirascope/GitHub/mirascope/mirascope/core/base/_extract.py:132, in extract_factory.<locals>.decorator.<locals>.inner(*args, **kwargs)
        130 except ValidationError as e:
        131     e._response = call_response  # pyright: ignore [reportAttributeAccessIssue]
    --> 132     raise e
        133 if isinstance(output, BaseModel):
        134     output._response = call_response  # pyright: ignore [reportAttributeAccessIssue]


    File ~/Mirascope/GitHub/mirascope/mirascope/core/base/_extract.py:129, in extract_factory.<locals>.decorator.<locals>.inner(*args, **kwargs)
        127 json_output = get_json_output(call_response, json_mode)
        128 try:
    --> 129     output = extract_tool_return(response_model, json_output, False)
        130 except ValidationError as e:
        131     e._response = call_response  # pyright: ignore [reportAttributeAccessIssue]


    File ~/Mirascope/GitHub/mirascope/mirascope/core/base/_utils/_extract_tool_return.py:38, in extract_tool_return(response_model, json_output, allow_partial)
         36 elif allow_partial:
         37     return partial(response_model).model_validate(json_obj)
    ---> 38 return response_model.model_validate(json_obj)


    File ~/Mirascope/GitHub/mirascope/.venv/lib/python3.10/site-packages/pydantic/main.py:551, in BaseModel.model_validate(cls, obj, strict, from_attributes, context)
        549 # `__tracebackhide__` tells pytest and some other tools to omit this function from tracebacks
        550 __tracebackhide__ = True
    --> 551 return cls.__pydantic_validator__.validate_python(
        552     obj, strict=strict, from_attributes=from_attributes, context=context
        553 )


    ValidationError: 2 validation errors for ValidatedBook
    title
      Assertion failed, All fields must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
        For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
    author
      Assertion failed, All fields must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
        For further information visit https://errors.pydantic.dev/2.7/v/assertion_error


We can see in this example that the model threw a `ValidationError` on construction because the extracted `title` and `author` fields were not all caps.

This example is of course for demonstration purposes. In a real-world example we would ensure we catch such errors and handle them gracefully as well as further engineer the prompt to ensure such errors occur rarely or not at all.

## Output Parsers

Mirascope also provides an `output_parser` argument that will run on the call response for every call. This enables writing prompts that have a more specific structure (such as Chain of Thought) while still ensuring the output has the desired structure:


```python
import re

from mirascope.core import prompt_template


def parse_cot(response: openai.OpenAICallResponse) -> tuple[str, str]:
    pattern = r"<thinking>(.*?)</thinking>.*?<output>(.*?)</output>"
    match = re.search(pattern, response.content, re.DOTALL)
    if not match:
        return "", response.content
    else:
        return match.group(1).strip(), match.group(2).strip()


@openai.call("gpt-4o-mini", output_parser=parse_cot)
@prompt_template(
    """
    SYSTEM:
    First, output your thought process in <thinking> tags.
    Then, provide your final output in <output> tags.

    USER: {query}
    """
)
def cot(query: str): ...


output = cot(
    "How many tennis balls does Roger have if he started with 2 and bought 3 tubes?"
)
print(f"Thinking: {output[0]}")
print(f"Output: {output[1]}")
```

    Thinking: To find out how many tennis balls Roger has, we first need to know how many balls are in a tube. A standard tube of tennis balls typically contains 3 balls. Given that Roger bought 3 tubes, we can calculate the total number of balls from the tubes by multiplying the number of tubes by the number of balls per tube. After that, we can add the 2 tennis balls he started with to find the total. So, the steps are:
    
    1. Calculate the total number of balls from the tubes: 3 tubes x 3 balls/tube = 9 balls.
    2. Add the 2 balls he started with to the total from the tubes: 2 + 9 = 11 balls.
    
    Thus, I will output the final answer that Roger has a total of 11 tennis balls.
    Output: Roger has 11 tennis balls.


## Conclusion

These techniques provide a solid foundation for structuring outputs in your LLM applications. As you continue to work with LLMs and develop more complex applications, robust prompt engineering and validation will be crucial for ensuring the quality and reliability of your models and outputs.

If you like what you've seen so far, [give us a star](https://github.com/Mirascope/mirascope) and [join our community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA).

For more advanced topics and best practices, refer to the Mirascope [Response Models](../../../learn/response_models) documentation, [JSON Mode](../../../learn/json_mode) documentation, and [Output Parsers](../../../learn/output_parsers) documentation.

We also recommend taking a look at our [Tenacity Integration](../../../learn/retries) to learn how to build more robust pipelines that automatically re-insert validation errors into a subsequent call, enabling the LLM to learn from its mistakes and (hopefully) output the correct answer on the next attempt.
