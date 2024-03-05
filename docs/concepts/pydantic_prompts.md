# Pydantic Prompts

The [`Prompt`](../api/base/prompt.md#mirascope.base.prompt.Prompt) class is the core of Mirascope, which extends Pydantic's [`BaseModel`](https://docs.pydantic.dev/latest/api/base_model/). The class leverages the power of python to make writing more complex prompts as easy and readable as possible. The docstring is automatically formatted as a prompt so that you can write prompts in the style of your codebase.

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


## The [`Prompt`](../api/base/prompt.md#mirascope.base.prompt.Prompt) Class

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
 
### Editor Support
* Inline Errors
![prompt-linting](https://github.com/Mirascope/mirascope/assets/15950811/4a1ebc7f-9f24-4106-a30c-87d68d88bf3c)
* Autocomplete
![prompt-autocomplete](https://github.com/Mirascope/mirascope/assets/15950811/a4c1e45b-d25e-438b-9d6d-b103c05ae054)

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

By default, the `Prompt` class treats the prompt template as a single user message. If you want to specify a list of messages instead, just use the message keywords SYSTEM, USER, ASSISTANT, or TOOL:

```python
from mirascope import Prompt


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
[{"role": "system", "content": "You are the world's greatest librarian"}, {"role": "user", "content": "Can you recommend some books on coding?"}]
```

### Tags and Dump

You can add tags to help organize prompts when you want to use them outside your project. For example, you might want to dump all your prompt inputs and outputs for validating prompt quality into a CSV file, or database. 

!!! note 
	
	`@tags` updates the `_tags` private attribute of the class with the provided list of tags, which you can access using the `tags` classmethod.

```python
from mirascope import OpenAIChat, Prompt, tags


@tags(["recommendation_project", "version:0001"])
class BookRecommendationPrompt(Prompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str


prompt = BookRecommendationPrompt(topic="how to bake a cake")
model = OpenAIChat()
print(prompt.dump())
# {'template': 'Can you recommend some books on {topic}?', 'inputs': {'topic': 'how to bake a cake'}, 'tags': ['recommendation_project', 'version:0001'], 'call_params': {'model': 'gpt-3.5-turbo-16k'}}
```

## Future updates

There is a lot more to be added to Mirascope prompts. Here is a list in no order of things we are thinking about adding next: 

- more complex prompts - handle more complex prompts for things like history
- testing for prompts - test the quality of your prompt input/output
- prompt response tracking - track the input/output when using a prompt

If you want some of these features implemented or if you think something is useful but not on this list, let us know!
