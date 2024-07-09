# Agents

If we take everything covered in the Usage section so far, we have the formula for a clean and intuitive agent interface. Access to the class’s attributes, properties, and other Pydantic functionalities let us manipulate stateful workflows with ease.

Here’s an example of a Librarian agent, with a full breakdown below.

```python
from typing import Literal

from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, Field

from mirascope.core import BasePrompt, anthropic, openai
from mirascope.core.base import BaseTool, BaseToolKit, toolkit_tool
from mirascope.integrations.tenacity import collect_validation_errors

class Book(BaseModel):
    title: str
    author: str

class CategorizedQuery(BaseModel):
    category: Literal["general", "reading_list", "book_rec"] = Field(
        ...,
        description="""The category of the query.
            general for generic chatting and questions.
            reading_list for explicit requests to modify or view reading list.
            book_rec for explicit book recommendation requests.""",
    )
    content: str = Field(..., description="The original text of the categorized query.")

class BookTools(BaseToolKit):
    reading_level: str

    @toolkit_tool
    def _recommend_book_by_level(self, title: str, author: str) -> str:
        """Returns the title and author of a book recommendation nicely formatted.

        Reading level: {self.reading_level} # Add highlight
        """
        return f"{title} by {author}."

class Librarian(BaseModel):
    _history: list[ChatCompletionMessageParam] = []
    reading_list: list[Book] = []

    def _add_to_reading_list(self, book: Book) -> str:
        """Add a book to the reading list."""
        if book not in self.reading_list:
            self.reading_list.append(book)
            return f"Added {book.title} to reading list."
        else:
            return f"Book {book.title} already in reading list."

    def _remove_from_reading_list(self, book: Book) -> str:
        """Remove a book from the reading list."""
        if book in self.reading_list:
            self.reading_list.remove(book)
            return f"Removed {book.title} from reading list."
        else:
            return f"Book {book.title} not in reading list."

    def _get_reading_list(self) -> str:
        """Gets the reading list."""
        return "\n".join([str(book) for book in self.reading_list])

    @retry(stop=stop_after_attempt(3), after=collect_validation_errors)
    @openai.call(model="gpt-4", response_model=CategorizedQuery)
    def _categorize_input(
        user_input: str, validation_errors: list[str] | None = None
    ) -> openai.OpenAIDynamicConfig:
        """
        {previous_errors}
        Categorize this input into one of the following:

        general - for general questions and chatting.
        reading_list - an explicit request to modify or view the user's reading list
        book_rec - an explicit request for a book recommendation

        input: {user_input}
        """
        return {
            "computed_fields": {
                "previous_errors": f"Previous errors: {validation_errors}"
                if validation_errors
                else ""
            }
        }

    @openai.call(model="gpt-4o", output_parser=str)
    def _summarize_reading_level(self) -> openai.OpenAIDynamicConfig:
        """
        Here is my reading list: {reading_list}
        Based on the books you see, describe my reading level. If my reading list is
        empty, just say "unknown". Respond with at most two words.
        """
        return {"computed_fields": {"reading_list": self.reading_list}}

    @openai.call(model="gpt-4o", stream=True)
    def _stream(self, query: CategorizedQuery) -> openai.OpenAIDynamicConfig:
        """
        SYSTEM:
        You are the world's greatest librarian.
        You are talking to someone with {reading_level} reading level.
        MESSAGES: {self._history}
        USER: {content}
        """
        reading_level = self._summarize_reading_level()
        if query.category == "book_rec":
            toolkit = BookTools(reading_level=reading_level)
            tools = toolkit.create_tools()
        elif query.category == "reading_list":
            tools = [
                self._add_to_reading_list,
                self._remove_from_reading_list,
                self._get_reading_list,
            ]
        else:
            tools = []
        return {
            "tools": tools,
            "computed_fields": {
                "reading_level": reading_level,
                "content": query.content,
            },
        }

    def _step(self, user_input: str):
        """Runs a single chat step with the librarian."""
        query = self._categorize_input(user_input)
        stream, tools_and_outputs = self._stream(query), []
        for chunk, tool in stream:
            if tool:
                output = tool.call()
                print(output)
                tools_and_outputs.append((tool, output))
            else:
                print(chunk, end="", flush=True)
        self._history += [
            stream.user_message_param,
            stream.message_param,
            *stream.tool_message_params(tools_and_outputs),
        ]

    def chat(self):
        """Runs a multi-turn chat with the librarian."""
        while True:
            user_input = input("You: ")
            if user_input in ["quit", "exit"]:
                break
            print("Librarian: ", end="", flush=True)
            self._step(user_input)
            print()

librarian = Librarian()
librarian.chat()
```

## Agent Structure

Relevant topics: decorating instance methods[link], message injection[link]

Let’s start analyzing the agent by looking at its general structure. We use our ability to decorate instance methods to create calls that can depend on state via the class attributes. 

`_stream()` is the core of the librarian which handles user’s input. We use Mirascope’s messages injection to give context/chat history to the prompt with the `MESSAGES` keyword:

```python
@openai.call(model="gpt-4o", stream=True)
def _stream(self, query: CategorizedQuery) -> openai.OpenAIDynamicConfig:
    """
    SYSTEM:
    You are the world's greatest librarian.
    You are talking to someone with {reading_level} reading level.
    MESSAGES: {self._history} # highlight
    USER: {content}
    """
```

 `_step()` represents a single interaction with the agent. After getting a response from `_stream()`, we update the `_history` attribute so consequent interactions are always up to date:

```python
 def _step(self, user_input: str):
        ...
        stream, tools_and_outputs = self._stream(query), []
        ...
        self._history += [
            stream.user_message_param,
            stream.message_param,
            *stream.tool_message_params(tools_and_outputs),
        ]
```

`run()` is a loop to keep the chat going and handle the I/O via command line.

## Categorizing Input

Relevant topics: Response Model[link], Retries[link]

A good use case for extraction[link] in our agent is to categorize the incoming user inputs so the agent can handle each input accordingly. We define the class `CategorizedQuery` so that we can handle 3 types of inputs. In `_step()`, before passing the input to `_stream()`, we categorize each input with the call `_categorize_input()` by setting `response_model=CategorizedQuery` in its decorator. Adding descriptions in the Pydantic `Field`s and retries with Mirascope’s tenacity integration helps ensure accurate and successful extractions, which we need since the agent depends on the ability to categorize input.

```python
class CategorizedQuery(BaseModel):
    category: Literal["general", "reading_list", "book_rec"] = Field(
        ...,
        description="""The category of the query.
            general for generic chatting and questions.
            ...
            """,
    )
    content: str = Field(..., description="The original text of the categorized query.")
...

class Librarian(BaseModel):
   ...

    @retry(stop=stop_after_attempt(3), after=collect_validation_errors)
    @openai.call(model="gpt-4", response_model=CategorizedQuery)
    def _categorize_input(
        user_input: str, validation_errors: list[str] | None = None
    ) -> openai.OpenAIDynamicConfig:
        """
        {previous_errors}
        Categorize this input into one of the following:

        general - for general questions and chatting.
        ...
        {input}
        """
        return {
            "computed_fields": {
                "previous_errors": f"Previous errors: {validation_errors}"
                if validation_errors
                else ""
            }
        }
     ...

    def _step(self, user_input: str):
        """Runs a single chat step with the librarian."""
        query = self._categorize_input(user_input)
        stream, tools_and_outputs = self._stream(query), []
        ...
       
```

## Dynamically Analyzed Reading Level

Relevant topics: Computed Fields[link], Chaining[link]

We can customize our librarian by letting them know of our reading level, dynamically analyzed from the books in our reading list. Separate prompts asking specific questions will yield more accurate results than asking several questions at once, so we create a new call `_summarize_reading_level()`. To incorporate its output into our primary function `_stream()`, we can chain the calls together with the `computed_fields` field in our dynamic configuration:

```python
class Librarian(BaseModel):
    _history: list[ChatCompletionMessageParam] = []
    reading_list: list[Book] = []

    @openai.call(model="gpt-4o", output_parser=str)
    def _summarize_reading_level(self) -> openai.OpenAIDynamicConfig:
        """
        Here is my reading list: {reading_list}
        Based on the books you see, describe my reading level. If my reading list is
        empty, just say "unknown". Respond with at most two words.
        """
        return {"computed_fields": {"reading_list": self.reading_list}}

    @openai.call(model="gpt-4o", stream=True)
    def _stream(self, query: CategorizedQuery) -> openai.OpenAIDynamicConfig:
        """
        SYSTEM:
        You are the world's greatest librarian.
        You are talking to someone with {reading_level} reading level.
        MESSAGES: {self._history}
        USER: {content}
        """
        reading_level = self._summarize_reading_level()
        ...
        return {
            "computed_fields": {
                "reading_level": reading_level
            },
        }
```

## Adding Our Tools

An agent without tools isn’t much more than a chatbot, so let’s incorporate some tools into our Librarian to give it functionality other than conversation. 

### Instance Methods

Relevant topics: Tools/Function Calling[link], Dynamic Configuration[link], Tools via Dynamic Configuration[link]

As instance methods, we have `_add_to_reading_list()`, `_remove_from_reading_list`, and `_get_reading_list()`, which do as they advertise to the class attribute `reading_list`. We take advantage of Mirascope’s dynamic configuration to (a) use these tools despite being instance methods, since dynamic configuration gives access to `self`, and (b) add our tools conditionally, limiting the chance of the model picking the wrong tool or using tools when it shouldn’t.

```python
class Librarian(BaseModel):
		...

    def _add_to_reading_list(self, book: Book) -> str:
        ...

    def _remove_from_reading_list(self, book: Book) -> str:
        ...

    def _get_reading_list(self) -> str:
        ...

    @openai.call(model="gpt-4o", stream=True)
    def _stream(self, query: CategorizedQuery) -> openai.OpenAIDynamicConfig:
        ...
        elif query.category == "reading_list":
            tools = [
                self._add_to_reading_list,
                self._remove_from_reading_list,
                self._get_reading_list,
            ]
        else:
            tools = []
        return {
            "tools": tools
        }
        
```

### ToolKit Tools

Relevant topics: ToolKit[link]

We also want a tool for recommending books, but we can improve that functionality by asking for a book recommendation in accordance with our reading level. We already dynamically retrieve our reading level from the current reading list, so we can create a `ToolKit` that takes `reading_level` as an input to dynamically generate a tool tailored to our needs. Just like the instance methods above, we can also make sure to only include it in our call when we have explicitly asked for a book recommendation.

```python
class BookTools(BaseToolKit):
    reading_level: str

    @toolkit_tool
    def _recommend_book_by_level(self, title: str, author: str) -> str:
        """Returns the title and author of a book recommendation nicely formatted.

        Reading level: {self.reading_level} # Add highlight
        """
        return f"{title} by {author}."
        
class Librarian(BaseModel):

    @openai.call(model="gpt-4o", output_parser=str)
    def _summarize_reading_level(self) -> openai.OpenAIDynamicConfig:
        ...

    @openai.call(model="gpt-4o", stream=True)
    def _stream(self, query: CategorizedQuery) -> openai.OpenAIDynamicConfig:
        ...
        reading_level = self._summarize_reading_level()
        if query.category == "book_rec":
            toolkit = BookTools(reading_level=reading_level)
            tools = toolkit.create_tools()
        else:
            tools = []
        return {
            "tools": tools,
            "computed_fields": {
                "reading_level": reading_level,
                "content": query.content,
            },
        }
```

This Librarian is just the tip of the iceberg of the kind of agents you can create with Mirascope’s primitives driven approach to LLM toolkits. For more inspiration, check out examples[link] and our cookbook[link]
