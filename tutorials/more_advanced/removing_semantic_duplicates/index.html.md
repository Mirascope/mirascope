# Removing Semantic Duplicates

 In this recipe, we show how to use LLMs — in this case, OpenAI's `gpt-4o-mini` — to answer remove semantic duplicates from lists and objects.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/response_models/">Response Model</a></li>
</ul>
</div>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p>
Semantic deduplication, or the removal of duplicates which are equivalent in meaning but not in data, has been a longstanding problem in NLP. LLMs which have the ability to comprehend context, semantics, and implications within that text trivializes this problem.
</p>
</div>

## Setup

Let's start by installing Mirascope and its dependencies:


```python
!pip install "mirascope[openai]"
```


```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Deduplicating a List

To start, assume we have a some entries of movie genres with semantic duplicates:


```python
movie_genres = [
    "sci-fi",
    "romance",
    "love story",
    "action",
    "horror",
    "heist",
    "crime",
    "science fiction",
    "fantasy",
    "scary",
]
```

To deduplicate this list, we’ll extract a schema containing `genres`, the deduplicated list, and `duplicates`, a list of all duplicate items. The reason for having `duplicates` in our schema is that LLM extractions can be inconsistent, even with the most recent models - forcing it to list the duplicate items helps it reason through the call and produce a more accurate answer.



```python
from pydantic import BaseModel, Field


class DeduplicatedGenres(BaseModel):
    duplicates: list[list[str]] = Field(
        ..., description="A list containing lists of semantically equivalent items"
    )
    genres: list[str] = Field(
        ..., description="The list of genres with semantic duplicates removed"
    )
```


We can now set this schema as our response model in a Mirascope call:



```python
from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini", response_model=DeduplicatedGenres)
@prompt_template(
    """
    SYSTEM:
    Your job is to take a list of movie genres and clean it up by removing items
    which are semantically equivalent to one another. When coming across multiple items
    which refer to the same genre, keep the genre name which is most commonly used.
    For example, "sci-fi" and "science fiction" are the same genre.

    USER:
    {genres}
    """
)
def deduplicate_genres(genres: list[str]): ...


response = deduplicate_genres(movie_genres)
assert isinstance(response, DeduplicatedGenres)
print(response.genres)
print(response.duplicates)
```

    ['action', 'horror', 'heist', 'crime', 'fantasy', 'scary']
    [['sci-fi', 'science fiction'], ['love story', 'romance']]



Just like with a list of strings, we can create a schema of `DeduplicatedBooks` and set it as the response model, with a modified prompt to account for the different types of differences we see:



```python
class Book(BaseModel):
    title: str
    author: str
    genre: str


duplicate_books = [
    Book(title="The War of the Worlds", author="H. G. Wells", genre="scifi"),
    Book(title="War of the Worlds", author="H.G. Wells", genre="science fiction"),
    Book(title="The Sorcerer's stone", author="J. K. Rowling", genre="fantasy"),
    Book(
        title="Harry Potter and The Sorcerer's stone",
        author="J. K. Rowling",
        genre="fantasy",
    ),
    Book(title="The Name of the Wind", author="Patrick Rothfuss", genre="fantasy"),
    Book(title="'The Name of the Wind'", author="Patrick Rofuss", genre="fiction"),
]


@openai.call(model="gpt-4o", response_model=list[Book])
@prompt_template(
    """
    SYSTEM:
    Your job is to take a database of books and clean it up by removing items which are
    semantic duplicates. Look out for typos, formatting differences, and categorizations.
    For example, "Mistborn" and "Mistborn: The Final Empire" are the same book 
    but "Mistborn: Shadows of Self" is not.
    Then return all the unique books.

    USER:
    {books}
    """
)
def deduplicate_books(books: list[Book]): ...


books = deduplicate_books(duplicate_books)
assert isinstance(books, list)
for book in books:
    print(book)
```

    title='The War of the Worlds' author='H. G. Wells' genre='scifi'
    title='War of the Worlds' author='H.G. Wells' genre='science fiction'


<div class="admonition tip">
<p class="admonition-title">Additional Real-World Examples</p>
<ul>
<li><b>Customer Relationship Management (CRM)</b>: Maintaining a single, accurate view of each customer.</li>
<li><b>Database Management</b>: Removing duplicate records to maintain data integrity and improve query performance</li>
<li><b>Email</b>: Clean up digital assets by removing duplicate attachments, emails.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider the following:

- Refine your prompts to provide clear instructions and examples tailored to your requirements.
- Experiment with different model providers and version to balance accuracy and speed.
- Use multiple model providers to evaluate whether all duplicates have bene removed.
- Add more information if possible to get better accuracy, e.g. some books might have similar names but are released in different years.

