# Writing prompts

## The [`BasePrompt`](../api/base/prompts.md#mirascope.base.prompts.BasePrompt) Class

The `prompt_template` class variable is the template used to generate the list of messages. The properties of the class are the template variables, which get formatted into the template during the creation of the list of messages.

```python
from mirascope import BasePrompt


class BookRecommendationPrompt(BasePrompt):
    prompt_template = "Can you recommend some books on {topic}?"

    topic: str


prompt = BookRecommendationPrompt(topic="coding")
print(prompt.messages())
#> [{"role": "user", "content": "Can you recommend some books on coding?"}]
```

The `messages` method parses the `prompt_template` into a list of messages. In this case, there's just a single user message.

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
    prompt_template = """
    Can you recommend some books on the following topic and genre pairs?
    {topics_x_genres}
    """

    topics: list[str]
    genres: list[str]

    @property
    def topics_x_genres(self) -> str:
        """Returns `topics` as a comma separated list."""
        return "\n".join(
            [
                f"Topic: {topic}, Genre: {genre}"
                for topic in self.topics
                for genre in self.genres
            ]
        )


prompt = BookRecommendationPrompt(
    topics=["coding", "music"], genres=["fiction", "fantasy"]
)
print(prompt)
#> Can you recommend some books on the following topic and genre pairs?
#  Topic: coding, Genre: fiction
#  Topic: coding, Genre: fantasy
#  Topic: music, Genre: fiction
#  Topic: music, Genre: fantasy
```

## Messages

By default, the `BasePrompt` class treats the prompt template as a single user message. If you want to specify a list of messages instead, use the message keywords SYSTEM, USER, ASSISTANT, MODEL, or TOOL (depending on what's supported by your choice of provider):

```python
from mirascope import BasePrompt


class BookRecommendationPrompt(BasePrompt):
	prompt_template = """
	SYSTEM:
	You are the world's greatest librarian.

	USER:
	Can you recommend some books on {topic}?
	"""

	topic: str


prompt = BookRecommendationPrompt(topic="coding")
print(prompt.messages())
```

```
[{"role": "system", "content": "You are the world's greatest librarian"}, {"role": "user", "content": "Can you recommend some books on coding?"}]
```

!!! note

    This example is using Mirascope base `Message. If you are using a different provider, refer to the provider's documentation on their message roles.

## Magic is optional

We understand that there are users that do not want to use template string magic. Mirascope allows the user to write the messages array manually, which has the added benefit of accessing functionality that is not yet supported by the template parser (such as Vision support).

```python
from mirascope import BasePrompt
from openai.types.chat import ChatCompletionMessageParam


class BookRecommendationPrompt(BasePrompt):
    topic: str

    def messages(self) -> list[ChatCompletionMessageParam]:
        return [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                        },
                    },
                ],
            },
        ]
```

## Integrations with Providers

The `BasePrompt` class should be used for providers that are not yet supported by Mirascope. Pass in the messages from the prompt into the LLM provider client messages array.

```python
from mirascope import BasePrompt
from some_llm_provider import LLMProvider


class BookRecommendationPrompt(BasePrompt):
	prompt_template = """
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
    messages=prompt.messages()
)
```
