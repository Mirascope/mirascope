# Response Models

Response Models in Mirascope provide a powerful way to structure and validate the output from Large Language Models (LLMs). By leveraging Pydantic's [`BaseModel`](https://docs.pydantic.dev/latest/usage/models/), Response Models offer type safety, automatic validation, and easier data manipulation for your LLM responses. While we cover some details in this documentation, we highly recommend reading through Pydantic's documentation for a deeper, comprehensive dive into everything you can do with Pydantic and `BaseModel`s.

## Why Use Response Models?

1. **Structured Output**: Define exactly what you expect from the LLM, ensuring consistency in responses.
2. **Automatic Validation**: Pydantic handles type checking and validation, reducing errors in your application.
3. **Improved Type Hinting**: Better IDE support and clearer code structure.
4. **Easier Data Manipulation**: Work with Python objects instead of raw strings or dictionaries.

## Using Response Models

To use a Response Model, define a Pydantic model and pass it to the `response_model` parameter in the `call` decorator:

```python hl_lines="5-7 10"
from mirascope.core import openai, prompt_template, Messages
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


@openai.call(model="gpt-4o-mini", response_model=Book)
@prompt_template()
def recommend_book(genre: str) -> Messages.Type:
    return f"Recommend a {genre} book"


book = recommend_book("science fiction")
assert isinstance(book, Book)
print(f"Title: {book.title}")
print(f"Author: {book.author}")
```

In this example:

1. We define a prompt template using the `@prompt_template()` decorator.
2. We wrap the function with the `@openai.call` decorator, specifying the model to use.
3. We set the `response_model` parameter to our `Book` class, which inherits from Pydantic's `BaseModel`.

This approach works consistently across all supported providers in Mirascope.

!!! tip "Accessing the Original Response"

    You can always access the original response through the `_response` property on the returned response model. However, this is a private attribute we've included for such access and is not an official property of the response model type, meaning that you'll need to ignore type errors when accessing the property and cast the property to get editor support on the original response object.

    Example:
    
    ```python hl_lines="2 4"
    # original `OpenAICallResponse`
    response = cast(openai.OpenAICallResponse, book._response)  # pyright: ignore [reportAttributeAccessIssue]
    # original `ChatCompletion`
    completion = response.response
    ```

## Extracting Built-in Types

For simpler cases where you want to extract just a single built-in type, Mirascope provides a shorthand:

```python hl_lines="1 7"
@openai.call("gpt-4o-mini", response_model=list[str])
@prompt_template()
def recommend_books(genre: str, num: int) -> Messages.Type:
    return f"Recommend a list of {num} {genre} books"


books = recommend_books("fantasy", 3)
for book in books:
    print(book)
# > The Name of the Wind by Patrick Rothfuss
#   Mistborn: The Final Empire by Brandon Sanderson
#   The Way of Kings by Brandon Sanderson
```

Here, we're using `list[str]` as the `response_model`, which Mirascope handles without needing to define a full `BaseModel`.

## Few-Shot Examples

Adding few-shot examples to your response model can improve results by demonstrating exactly how to adhere to your desired output:

```python hl_lines="9-15 18"
from mirascope.core import openai, prompt_template
from pydantic import BaseModel, ConfigDict, Field


class Book(BaseModel):
    title: str = Field(..., examples=["THE NAME OF THE WIND"])
    author: str = Field(..., examples=["Rothfuss, Patrick"])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
            ]
        }
    )


@openai.call("gpt-4o-mini", response_model=Book, json_mode=True)
@prompt_template()
def recommend_book(genre: str) -> Messages.Type:
    return f"Recommend a {genre} book. Match example format."


book = recommend_book("scifi")
print(book)
# > title='DUNE' author='Herbert, Frank'
```

This example demonstrates:

1. Using `Field` to provide examples for individual fields.
2. Using `ConfigDict` to provide a full example of the model structure.
3. Setting `json_mode=True` to improve the effectiveness of examples.

!!! note "Example Effectiveness"

    We have found that examples are more effective when used in conjunction with additional prompt engineering. In the above example, you can see that we added "Match example format" to the prompt. We have also found that examples often work better when using `json_mode=True`. We believe that this is the result of models not being trained specifically on JSON schemas with examples and more often trained on few-shot examples that are directly part of the prompt itself.

## Streaming Response Models

If you set `stream=True` when `response_model` is set, your LLM call will return an `Iterable` where each item will be a partial version of your response model representing the current state of the streamed information. The final model returned by the iterator will be the full response model.

```python hl_lines="10 17 18"
from mirascope.core import openai, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


@openai.call(model="gpt-4o-mini", response_model=Book, stream=True)
@prompt_template()
def recommend_book(genre: str) -> Messages.Type:
    return f"Recommend a {genre} book"


book_stream = recommend_book("science fiction")
for partial_book in book_stream:
    print(partial_book)
# title=None author=None
# title=None author=None
# title='' author=None
# title='D' author=None
# title='Dune' author=None
# title='Dune' author=None
# title='Dune' author=None
# title='Dune' author=''
# title='Dune' author='Frank'
# title='Dune' author='Frank Herbert'
# title='Dune' author='Frank Herbert'
# title='Dune' author='Frank Herbert'
# title='Dune' author='Frank Herbert'
```

### Type Safety with Response Models

When using response models with Mirascope's `call` decorator, you benefit from enhanced type safety and accurate type hints. The decorator ensures that the return type of your function matches the response model you specify.

In the above example, your IDE will provide proper autocompletion and type checking for `recommendation.title` and `recommendation.author`, enhancing code reliability and developer productivity.

## JSON Mode and Response Models

When using Response Models, the default setting is `json_mode=False`, which will use [`Tools`](./tools.md) under the hood to perform the structured output extraction. However, for some providers setting `json_mode=True` enables support for field types that may not be supported by tools.

```python hl_lines="8"
from mirascope.core import openai, prompt_template
from pydantic import BaseModel

class BookOutline(BaseModel):
    title: str
    chapters: list[str]

@openai.call("gpt-4o-mini", response_model=BookOutline, json_mode=True)
@prompt_template()
def outline_book(genre: str) -> Messages.Type:
    return f"Outline a {genre} book with chapter titles"

book_outline = outline_book("mystery")
print(f"Title: {book_outline.title}")
print("Chapters:")
for chapter in book_outline.chapters:
    print(f"- {chapter}")
```

!!! note "Not All Providers Have Explicit JSON Mode Support"

    In cases where a model provider does not have explicit JSON Mode support, Mirascope implements a pseudo JSON Mode by instructing the model to output JSON in the prompt. Since all providers support [`Tools`](./tools.md), the default when using `response_model` is `json_mode=False`.

We generally recommend testing both settings to see which works better for your use-case. For more details on JSON Mode, refer to the [JSON Mode documentation](./json_mode.md).

### Field Type Support Across Providers

The support for different field types varies across providers. Here's a comprehensive overview:

|     Type      | Anthropic | Cohere | Gemini | Groq | Mistral | OpenAI |
|---------------|-----------|--------|--------|------|---------|--------|
|     str       |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     int       |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|    float      |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     bool      |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     bytes     |✓✓|✓✓|-✓|✓✓|✓✓|✓✓|
|     list      |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     set       |✓✓|✓✓|--|✓✓|✓✓|✓✓|
|     tuple     |✓✓|✓✓|-✓|✓✓|✓✓|-✓|
|     dict      |✓✓|✓✓|✓✓|✓✓|✓✓|-✓|
|  Literal/Enum |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|   BaseModel   |✓✓|-✓|✓✓|✓✓|✓✓|✓✓|
| Nested ($def) |✓✓|--|--|✓✓|✓✓|✓✓|

✓✓ : Fully Supported, -✓: Only JSON Mode Support, -- : Not supported

## Error Handling and Validation

While Response Models significantly improve output structure and validation, it's important to handle potential errors:

```python hl_lines="3 6"
from pydantic import ValidationError

try:
    response = recommend_book("science fiction")
    print(response.title)
except ValidationError as e:
    print(f"Validation error: {e}")
```

For robust applications, consider implementing retry logic with validation error feedback. Check out the [Tenacity integration documentation](../integrations/tenacity.md) to learn how to easily reinsert validation errors into subsequent retry calls.

### Accessing Original Response On Error

In case of a `ValidationError`, you can access the original response for debugging:

```python hl_lines="26 32 33"
from typing import cast

from mirascope.core import openai, prompt_template
from pydantic import BaseModel, ValidationError, field_validator


class Book(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def isupper(cls, title: str) -> str:
        if not title.isupper():
            raise ValueError(f"title is not uppercase: {title}")
        return title


@openai.call("gpt-4o-mini", response_model=Book)
@prompt_template()
def recommend_book(genre: str) -> Messages.Type:
    return f"Recommend a {genre} book"

try:
    book = recommend_book("fantasy")
    print(book)
except ValidationError as e:
    print(e)
    # > 1 validation error for Book
    #   title
    #     Value error, title is not uppercase: The Name of the Wind [type=value_error, input_value='The Name of the Wind', input_type=str]
    #       For further information visit https://errors.pydantic.dev/2.7/v/value_error
    response = cast(openai.OpenAICallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
    print(response.model_dump())
    # > {'metadata': {}, 'response': {'id': ...}, ...}
```

This allows you to inspect the raw LLM response when validation fails.

## Best Practices

Here are some best practices to follow when using Response Models:

1. **Use Clear Field Names**: Choose descriptive names for your model fields to guide the LLM's output.
   ```python
   class BookReview(BaseModel):
       book_title: str
       author_name: str
       rating: int
       review_text: str
   ```

2. **Provide Field Descriptions**: Use Pydantic's `Field` with descriptions to give the LLM more context.
   ```python
   class MovieRecommendation(BaseModel):
       title: str = Field(..., description="The full title of the movie")
       director: str = Field(..., description="The name of the movie's director")
       year: int = Field(..., description="The year the movie was released")
       genre: str = Field(..., description="The primary genre of the movie")
   ```

3. **Start Simple**: Begin with basic types and gradually increase complexity as needed.
   ```python
   # Start with this:
   class SimpleRecipe(BaseModel):
       name: str
       ingredients: list[str]

   # Then evolve to this:
   class DetailedRecipe(BaseModel):
       name: str
       ingredients: list[Ingredient]
       preparation_time: int
       cooking_time: int
       instructions: list[str]
   ```
4. **Handle Errors Gracefully**: Implement proper error handling and consider using retry mechanisms.
   ```python
   from tenacity import retry, stop_after_attempt, wait_fixed

   @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
   @openai.call("gpt-4o-mini", response_model=Recipe)
   @prompt_template()
   def get_recipe(dish: str) -> Messages.Type:
       return f"Provide a recipe for {dish}"

   try:
       recipe = get_recipe("spaghetti carbonara")
       print(recipe)
   except Exception as e:
       print(f"Failed to get recipe after retries: {e}")
   ```

   For more advanced error handling techniques, check out our [Tenacity integration documentation](../integrations/tenacity.md).
 
5. **Leverage JSON Mode**: When possible, use `json_mode=True` for better type support and consistency.
   ```python
   @openai.call("gpt-4o-mini", response_model=ComplexDataStructure, json_mode=True)
   @prompt_template()
   def get_complex_data(query: str) -> Messages.Type:
       return f"Generate complex data for {query}"
   ```

6. **Test Thoroughly**: Validate your Response Models across different inputs and edge cases.
   ```python
   import pytest
 
   class Book(BaseModel):
       title: str
       author: str
       genre: str
   
   @openai.call("gpt-4o-mini", response_model=Book)
   @prompt_template()
   def recommend_book(genre: str) -> Messages.Type:
       return f"Recommend a {genre} book"
   
   @openai.call("gpt-4o-mini", response_model=bool)
   @prompt_template("""
   Validate if the following book recommendation is appropriate and accurate:
   Genre requested: {requested_genre}
   Book recommended: {book.title} by {book.author} (Genre: {book.genre})
   
   Consider the following:
   1. Does the recommended book's genre match or closely relate to the requested genre?
      2. Is the book title and author combination valid and real?
      3. Is the recommendation appropriate for general audiences?
   
   Respond with True if the recommendation is valid and appropriate, False otherwise.
   """)
   def validate_recommendation(book: Book, requested_genre: str):
       ...
   
   @pytest.mark.parametrize("genre", [
       "sci-fi", "romance", "mystery", "non-fiction",
       "children's", "18+ only", "nonsensical genre",
       "very very very long genre name that is unlikely to be recognized"
   ])
   def test_book_recommendation(genre):
       book = recommend_book(genre)
   
       is_valid = validate_recommendation(
           book=book,
           requested_genre=genre,
       )
   
       assert is_valid, f"Invalid recommendation for genre '{genre}': {book.title} by {book.author} (Genre: {book.genre})"

       # Additional specific checks can be added here if needed
       assert len(book.title) > 0, "Book title should not be empty"
       assert len(book.author) > 0, "Book author should not be empty"
   ```

By following these best practices and leveraging Response Models effectively, you can create more robust, type-safe, and maintainable LLM-powered applications with Mirascope.
