# Writing prompts

## The [`BasePrompt`](../api/base/prompt.md#mirascope.base.prompts.BasePrompt) Class

The docstring of the class acts as the prompt's template, and the attributes act as the template variables:

```python
from mirascope import BasePrompt


class BookRecommendationPrompt(BasePrompt):
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
from mirascope import BasePrompt


class LongerPrompt(BasePrompt):
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

## Editor Support

- Inline Errors
    
    ![https://github.com/Mirascope/mirascope/assets/15950811/4a1ebc7f-9f24-4106-a30c-87d68d88bf3c](https://github.com/Mirascope/mirascope/assets/15950811/4a1ebc7f-9f24-4106-a30c-87d68d88bf3c)
    
- Autocomplete
    
    ![https://github.com/Mirascope/mirascope/assets/15950811/a4c1e45b-d25e-438b-9d6d-b103c05ae054](https://github.com/Mirascope/mirascope/assets/15950811/a4c1e45b-d25e-438b-9d6d-b103c05ae054)
    

## Template Variables

When you call `str(prompt)` the template will be formatted using the properties of the class that match the template variables. This means that you can define more complex properties through code. This is particularly useful when you want to inject template variables with custom formatting or template variables that depend on multiple attributes.

```python
from mirascope import BasePrompt


class BookRecommendationPrompt(BasePrompt):
    """
    Can you recommend some books on the following topic and genre pairs?

		{topics_x_genres}
    """

    topics: list[str]
		genres: list[str]

    @property
    def topics_x_genres(self) -> str:
        """Returns `topics` as a comma separated list."""
        return "\\n\\t".expandtabs(4).join(
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

## Messages

By default, the `Prompt` class treats the prompt template as a single user message. If you want to specify a list of messages instead, use the message keywords SYSTEM, USER, ASSISTANT, or TOOL:

```python
from mirascope import BasePrompt


class BookRecommendationPrompt(BasePrompt):
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

!!! note

    This example is using OpenAI messages, if you are using a different provider, refer to the provider's documentation on their message roles.

## Magic is optional

We understand that there are users that do not want to use docstring magic. Mirascope allows the user to write the messages array manually, which has the added benefit of accessing functionality that is not yet supported by the docstring parser.

```python
from mirascope import BasePrompt
from openai.types.chat import ChatCompletionMessageParam


class BookRecommendationPrompt(BasePrompt):
    """A normal docstring"""

    topic: str
    history: list[Message] = []

    @property
    def messages(self) -> list[ChatCompletionMessageParam]:
        return [
            {"role": "system", "content": "You are the world's greatest librarian."},
            *self.history,
            {"role": "user", "content": f"Can you recommend some books on {self.topic}?"},
        ]
```

## Integrations with Providers

The `BasePrompt` class should be used for providers that are not yet supported by Mirascope. Pass in the messages from the prompt into the LLM provider client messages array.

```python
from mirascope import BasePrompt
from some_llm_provider import LLMProvider


class BookRecommendationPrompt(BasePrompt):
	"""
	SYSTEM:
	You are the world's greatest librarian.

	USER:
	Can you recommend some books on {topic}?
	"""

	topic: str


prompt = BookRecommendationPrompt(topic="coding")
client = LLMProvider(api_key=...)
message = client.messages.create(
    model="some-model",
    max_tokens=1000,
    temperature=0.0,
		stream=False,
    messages=prompt.messages
)
```
