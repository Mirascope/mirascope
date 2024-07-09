# Chaining Calls

When chaining multiple calls with Mirascope, we recommend you use computed fields to colocate the metadata of all calls along the chain.

Directly passing the output of one call as input to the next does work (as it is just Python), but you miss out on the ability to see all relevant inputs from one location.

## Using Calls

When using Mirascope’s decorated functions, set the output of the previous call as a computed field.

```python
from mirascope.core import openai

@openai.call(model="gpt-4o", temperature=0.4)
def recommend_author(genre: str):
    """Who is the greatest {genre} author?. Give just the name."""

@openai.call(model="gpt-4o")
def recommend_book(genre: str):
    """Recommend a {genre} book by {author}."""
    return {"computed_fields": {"author": recommend_author(genre)}}
    
    
response = recommend_book(genre="fantasy")
print(response.content)
# > Certainly! "The Hobbit" is one of J.R.R. Tolkien's greatest works...
```

Mirascope’s response objects are built on top Pydantic, so responses are serializable with the `model_dump()` method.  With computed fields, the serialization becomes a nested dictionary structure you can navigate from the final response to see relevant metadata from the calls along the chain.

```python
recommend_book_dump = response.model_dump()

print(recommend_book_dump)
# > {
#     'call_params': {}
#     ...
#     'fn_return': {
#       'computed_fields': {
#         'author': {
#           'call_params': {'temperature': 0.4},
#           'cost': 0.00017,
#           ...
#         }
#       }
#     }

recommend_author_dump = recommend_book_dump["fn_return"]["computed_fields"]["author"]

print(recommend_author_dump["call_params"]["temperature"])
# > 0.4

print(recommend_author_dump["cost"])
# > 0.00017

print(recommend_author_dump["prompt_template"])
# > Who is the greatest {genre} author?. Give just the name.
```

## Using BasePrompt

Using `BasePrompt` follows the same concept, but instead we use Pydantic’s `computed_field` decorator to make sure previous calls are included in the dump. We can type `author` to return an `OpenAICallResponse` since the parser will call `str()` on it before being formatted into the prompt.

```python
from pydantic import computed_field
from mirascope.core import BasePrompt
from mirascope.core.openai import OpenAICallResponse

class AuthorRecommendationPrompt(BasePrompt):
    """Recommend an author for {genre}. Give just the name."""

    genre: str

class BookRecommendationPrompt(BasePrompt):
    """Recommend a {genre} book by {author}."""

    genre: str

    @computed_field
    def author(self) -> OpenAICallResponse:
        response = AuthorRecommendationPrompt(genre=self.genre).run(
            openai.call("gpt-4o")
        )
        return response

book_recommendation_prompt = BookRecommendationPrompt(genre="fantasy")
response = book_recommendation_prompt.run(openai.call("gpt-4o"))
print(response.content)
# > , I highly recommend "Mistborn: The Final Empire" by Brandon Sanderson...
```

Dumping the response with `model_dump` shows the previous call in its serialization:

```python
recommend_book_dump = response.model_dump()

print(recommend_book_dump)
# > {
#     ...
#     'author': {
#       'tags': [],
#       `response`: {
#           "created": 1719513410,
#           "model": "gpt-4o-2024-05-13",
#         ...
#       }
#       "prompt_template": "Recommend an author for {genre}. Give just the name.",
#       ...
#     }
#   }
```

!!! Note: The serialization from `model_dump` will differ between calls and `BasePrompt`, so navigate accordingly.

## Without Computed Fields

Since Mirascope is just Python, nothing is stopping you from sequentially passing the output of one call to the next:

```python
@openai.call(model="gpt-4o", temperature=0.4)
def recommend_author(genre: str):
    """Who is the greatest {genre} author?. Give just the name."""

@openai.call(model="gpt-4o")
def recommend_book(genre: str, author: str):
    """Recommend a {genre} book by {author}."""
    
genre = "fantasy"
author_response = recommend_author(genre=genre)
author = author_response.content
book_response = recommend_book(genre=genre, author=author)
book = book_response.content
```

```python
class AuthorRecommendationPrompt(BasePrompt):
    """Recommend an author for {genre}. Give just the name."""

    genre: str

class BookRecommendationPrompt(BasePrompt):
    """Recommend a {genre} book by {author}."""

    genre: str
    author: str

genre = "fantasy"
author_prompt = AuthorRecommendationPrompt(genre=genre)
author_response = author_prompt.run(openai.call("gpt-4o"))
author = author_response.content
book_prompt = BookRecommendationPrompt(genre=genre, author=author)
book_response = book_prompt.run(openai.call("gpt-4o"))
book = book_response.content
```

In both cases, `book_response.model_dump()` will display the text output of *only* the previous call - without serialization, you will not be able to see the output or metadata of earlier calls in a chain of 3 or more calls without dumping each response manually.

## More Examples

By incorporating more complex logic with computed fields, you can easily write more complex flows such as conditional chaining[link], parallel chaining[link], and more[link].
