# Tools (Function Calling)

Generally, using tools/function calling with LLMs requires writing a schema to represent the function you want to call. With Mirascope, you can use functions directly as tools and let us convert the function into its corresponding provider-specific schema.

For any function(s), put them in a list and pass them into the decorator as the `tools` argument:

```python
from mirascope.core import openai

def format_book(title: str, author: str) -> str:
    """Returns the title and author of a book nicely formatted.
    
    Args:
        title: The title of the book.
        author: The author of the book in all caps.
    """
    return f"{title} by {author}"
    
@openai.call(model="gpt-4o", tools=[format_book], tool_choice="required")
def recommend_book(genre: str):
    """Recommend a {genre} book."""
    
tool = recommend_book("fantasy").tool  # `format_book` tool instance
print(tool.call())  # runs `format_book` with `title` and `author` args
# > The Name of the Wind by PATRICK ROTHFUSS
```

Under the hood we convert the function definition into a `BaseTool` definition by parsing the function’s signature and docstring. They will be included in the schema Mirascope generates and sends to the model. We currently support ReST, Google, Numpydoc-style and Epydoc docstrings.

You can also define your own `BaseTool` schema, and it will work across the providers we support.

```python
from mirascope.core import BaseTool
from pydantic import Field

class FormatBook(BaseTool):
    """Returns the title and author of a book nicely formatted."""
    
    title: str = Field(..., description="The title of the book.")
    author: str = Field(..., description="The author of the book in all caps.")
    
    def call(self) -> str:
        return f"{title} by {author}"
```

## Tools via Dynamic Configuration

Tools can also be specified via Mirascope’s dynamic configuration by adding the `tools` key to the return structure. This is necessary when:

- the call and tool are both instance methods of a class and the tool needs access to `self`
- the tool is dynamically generated from the input or from an attribute (explained further down in the `ToolKit` section

```python
class Librarian(BaseModel):
    reading_list: list[str] = []

    def _add_to_reading_list(self, book_title: str) -> str:
        """Returns the book after adding it to the reading list."""
        self.reading_list.append(book_title)
        return book_title

    @openai.call("gpt-4o", tool_choice="required")
    def recommend_book(self, genre: str) -> openai.OpenAIDynamicConfig:
        """
        SYSTEM: You are the world's greatest librarian.
        USER: Add a {genre} book to my reading list.
        """
        return {"tools": [self._add_to_reading_list]}
```

## Async

Tools operate the same way for both sync and async calls.

```python
import asyncio
from mirascope.core import openai

def format_book(title: str, author: str) -> str:
    """Returns the title and author of a book nicely formatted.

    Args:
        title: The title of the book.
        author: The author of the book in all caps.
    """
    return f"{title} by {author}"

@openai.call_async(model="gpt-4o", tools=[format_book], tool_choice="required")
async def recommend_book(genre: str):
    """Recommend a {genre} book."""

async def run():
    response = await recommend_book("fantasy")
    if tool := response.tool:
        print(tool.call())

asyncio.run(run())
# > The Name of the Wind by PATRICK ROTHFUSS
```

## Streaming

Tools can also be used in streamed calls. Mirascope stream responses return a tuple of instances of `(Type[BaseCallResponseChunk], Type[BaseTool] | None)`, so iterate through the stream and call the tool when it becomes available:

```python
from mirascope.core import openai

def format_book(title: str, author: str) -> str:
    """Returns the title and author of a book nicely formatted.
    
    Args:
        title: The title of the book.
        author: The author of the book in all caps.
    """
    return f"{title} by {author}"
    
@openai.call(model="gpt-4o", tools=[format_book], tool_choice="required")
def recommend_book(genre: str):
    """Recommend a {genre} book."""

results = recommend_book(genre="fantasy")
for chunk, tool in results: # Add highlight
    if tool:
        print(tool.call())
    else: 
        print(chunk.content, end="", flush=True)
# > The Name of the Wind by PATRICK ROTHFUSS 
```

## Few Shot Examples

If you want to add few shot examples to increase the accuracy of the model’s tool response, you can do so via `BaseTool` since it inherits from Pydantic `BaseModel`. Use the `examples` argument of Pydantic’s `Field` to set examples for individual attributes or the `model_config` to set up examples of all arguments.

```python
from pydantic import ConfigDict
from mirascope.core.base import BaseTool

class FormatBook(BaseTool):
    """Returns the title and author of a book nicely formatted."""
    
    title: str = Field(
        ..., description="The title of the book.", examples=["The Name of the Wind"]
    )
    author: str = Field(
        ...,
        description="The author of the book in all caps.",
        examples=["Rothfuss, Patrick"],
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "The Name of the Wind", "author": "Rothfuss, Patrick"}
            ]
        }
    )
    
    def call(self) -> str:
        return f"{title} by {author}"
```

You can provide examples for the entire model when using functions as tools. Simply add JSON examples that can be loaded into the `model_config`:

```python
from mirascope.core import openai


def format_book(title: str, author: str) -> str:
    """Returns a formatted book recommendation.

    Example:
        {"title": "THE HOBBIT", "author": "J.R.R. Tolkien"}

    Example:
        {"title": "THE NAME OF THE WIND", "author": "Patrick Rothfuss"}

    Args:
        title: The title of the book.
        author: The author of the book.
    """
    return f"Sure! I would recommend {title} by {author}."
```

## ToolKit

Mirascope’s `ToolKit` class allows you to dynamically generate functions to be used as tools  with additional configurations. Its functionality is best explained via an example:

```python
from mirascope.core import openai
from mirascope.core.base import BaseToolKit, toolkit_tool

class BookTools(BaseToolKit):
    reading_level: Literal["beginner", "intermediate", "advanced"]

    @toolkit_tool
    def _recommend_book_by_level(self, title: str, author: str) -> str:
        """Returns the title and author of a book recommendation nicely formatted.

        Reading level: {self.reading_level} # Add highlight
        """
        return f"A {title} by {author}"

class Librarian(BaseModel):
    user_reading_level: Literal["beginner", "intermediate", "advanced"]

    @openai.call("gpt-4o", tool_choice="required")
    def recommend_book(self, genre: str):
        """
        SYSTEM: You are the world's greatest librarian.
        USER: Recommend a {genre} book.
        """
        toolkit = BookTools(reading_level=self.user_reading_level)
        tools = toolkit.create_tools()
        return {"tools": tools}

kids_librarian = Librarian(user_reading_level="beginner")
print(kids_librarian.recommend_book(genre="science").tool.call())
# > Astrophysics for Young People in a Hurry by Neil deGrasse Tyson

phd_librarian = Librarian(user_reading_level="advanced")
print(phd_librarian.recommend_book(genre="science").tool.call())
# > A Brief History of Time by Stephen Hawking
```

- To make your own toolkit, define a class subclassed to  `ToolKit`.
- Give it any attributes, properties, or Pydantic functionalities you want (since it’s built on `BaseModel`)
- Decorate functions with `toolkit_tool` if you’d like them to become available as tools. Functions’ docstrings will be parsed with template variables, allowing you to dynamically modify the tool’s description using attributes of the `Toolkit`.
- Call `create_tools()` on an instance of your toolkit to generate a list of tools which can be passed to your call.
