# Pydantic Prompts

The [`Prompt`](../api/prompts.md#mirascope.prompts.Prompt) class is the core of Mirascope, which extends Pydantic's [`BaseModel`](https://docs.pydantic.dev/latest/api/base_model/). The class leverages the power of python to make writing more complex prompts as easy and readable as possible. The docstring is automatically formatted as a prompt so that you can write prompts in the style of your codebase.

## Why should you care?

- You get all of the [benefits of using Pydantic](https://docs.pydantic.dev/latest/#why-use-pydantic):
    - type hints, json schema, customization, ecosystem, production-grade
- Speeds up development
    - Fewer bugs through validation
    - Auto-complete, editor (and linter) support for errors
- Easy to learn
		- You only need to learn Pydantic
- Standardization and compatibility
    - Integrations with other libraries that use JSON Schema such as OpenAPI and FastAPI means writing less code.
- Customization
    - Everything is Pydantic or basic python, so changing anything is as easy as overriding what you want to change
- **All of the above helps lead to production ready code**


## The [`Prompt`](../api/prompts.md#mirascope.prompts.Prompt) Class

The docstring of the class acts as the prompt's template, and the attributes act as the template variables:

```python
from mirascope import Prompt

class BookRecommendationPrompt(Prompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str

prompt = BookRecommendationPrompt(topic="coding")
str(prompt)
```

```
Can you recommend some books on coding?
```

The `__str__` method, which formats all of the template variables, relies on the `template` function, which provides built-in string formatting so that you can write prettier docstrings. This means that longer prompts will still look well-formatted in your code base:

```python
class LongerPrompt(Prompt):
	"""
	Longer prompts can be edited in a more organized format that looks
	better in your code base. Any unwanted characters such as newlines
	or tabs that are purely for text alignment and structure will be 
	automatically removed.

	For newlines, just add one extra (e.g. 2 newlines -> 1 newline here)

		- The same goes for things you want indented
	"""
```

!!! note

	If you want custom docstring formatting or none at all, simply override the `template` method.

### Template Variables

When you call `str(prompt)` the template will be formatted using the properties of the class that match the template variables. This means that you can define more complex properties through code. This is particularly useful when you want to inject template variables with custom formatting or template variables that depend on multiple attributes. 

```python
from mirascope import Prompt

class BookRecommendationPrompt(Prompt):
    """
    Can you recommend some books on the following topic and genre pairs?

		{topics_x_genres}
    """

    topics: list[str]
	genres: list[str]

    @property
    def topics_x_genres(self) -> str:
        """Returns `topics` as a comma separated list."""
        return "\n\t".expandtabs(4).join(
            [
                f"Topic: {topic}, Genre: {genre}"
                for topic in self.topics
                for genre in self.genres
            ]
        )

prompt = BookRecommendationPrompt(
	topics=["coding", "music"], genres=["fiction", "fantasy"]
)
str(prompt)
```

```
Can you recommend some books on the following topic and genre pairs?
	Topic: coding, Genre: fiction
	Topic: coding, Genre: fantasy
	Topic: music, Genre: fiction
	Topic: music, Genre fantasy
```

### Messages

By default, the `Prompt` class treats the prompt template as a single user message. If you want to specify a list of messages instead, we provide a decorator to make this easy:

!!! note 
	
	`@messages` decorator adds `messages` property to the class

```python
from mirascope import messages, Prompt

@messages
class BookRecommendationPrompt(Prompt):
	"""
	SYSTEM:
	You are the world's greatest librarian.

	USER:
	Can you recommend some books on {topic}?
	"""

	topic: str

prompt = BookRecommendationPrompt(topic="coding")
print(prompt.messages)
```

```
[("system", "You are the world's greatest librarian"), ("user", "Can you recommend some books on coding?")]
```

### Future updates

There is a lot more to be added to Mirascope prompts. Here is a list in no order of things we are thinking about adding next: 

- more complex prompts - handle more complex prompts for things like history
- testing for prompts - test the quality of your prompt input/output
- prompt response tracking - track the input/output when using a prompt

If you want some of these features implemented or if you think something is useful but not on this list, let us know!
