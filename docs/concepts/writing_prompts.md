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

    ![missing-arguments](../images/prompt_missing_arguments.png)

- Autocomplete

    ![autocomplete](../images/prompt_autocomplete.png)

## Template Variables

When you call `prompt.messages()` or `str(prompt)` the template will be formatted 
using the fields and properties of the class that match the template variables. This means that you can define more complex properties through code using the [built in python decorator](https://docs.python.org/3/library/functions.html#property) `@property`. This is particularly useful when you want to inject template variables with custom formatting or template variables that depend on multiple attributes.

```python
from mirascope import BasePrompt

class BasicAddition(BasePrompt):
    prompt_template = """
    Can you solve this math problem for me?
    {equation}
    """
    first_number: float
    second_number: float

    @property
    def equation(self) -> str:
        return f"{self.first_number}+{self.second_number}="

addition_prompt = BasicAddition(first_number=6, second_number=10)
print(addition_prompt.equation)
#> 6.0+10.0=
print(addition_prompt)
#> Can you solve this math problem for me?
#  6.0+10.0=
print(addition_prompt.dump())
#> {
#       "tags": [],
#       "template": "Can you solve this math problem for me?\n{addition_equation}",
#       "inputs": {"first_number": 6.0, "second_number": 10.0},
#  }
```

If the type being returned is a list we will automatically format `list` and `list[list]` fields and properties with `\n` and `\n\n` separators, respectively and stringify.

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
    def topics_x_genres(self) -> list[str]:
        """Returns `topics` as a comma separated list."""
        return [
            f"Topic: {topic}, Genre: {genre}"
            for topic in self.topics
            for genre in self.genres
        ]


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

By default, the `BasePrompt` class treats the prompt template as a single user message. If you want to specify a list of messages instead, use the message keywords SYSTEM, USER, ASSISTANT, MODEL, TOOL, and more (depending on what's supported by your choice of provider):

```python
from mirascope import BasePrompt


class BookRecommendationPrompt(BasePrompt):
    prompt_template = """
    SYSTEM: You are the world's greatest librarian.
    USER: Can you recommend some books on {topic}?
    """

    topic: str


prompt = BookRecommendationPrompt(topic="coding")
print(prompt.messages())
```

```python
[{"role": "system", "content": "You are the world's greatest librarian"}, {"role": "user", "content": "Can you recommend some books on coding?"}]
```

Notice how all the surrounding white space is stripped so you can have a human-readable template without using more input tokens for the call.

!!! note

    This example is using Mirascope base `Message`. If you are using a different provider, refer to the provider's documentation on their message roles.

!!! warning

    Note that the parser will only parse expected keyword roles available to the provider. This ensures that keywords like `KEYWORD:` will not accidentally get parsed as a role; however, this also means that typos such as `USERS:` will also not get parsed.

    We are working on a VSCode extension to help identify these common typos and avoid potentially annoying silent bugs.

### Multi-Line Messages

When writing longer, multi-line prompts, the prompt template parser expects the content for each role to start on a new line below the role keyword so that e.g. tabs can be properly dedented. The newline between each role is optional but provides additional readability.

```python
from mirascope import BasePrompt


class BookRecommendationPrompt(BasePrompt):
    prompt_template = """
    SYSTEM:
    When writing longer, multi-line prompts, start content on a new line.
    This will ensure the content gets properly parsed and dedented.

    USER:
    The additional new line above between the roles is optional.
    However, we find this provides additional readability.
    """
```

## Prompt template "magic" is optional

We understand that there are users that do not want to use prompt template string parsing "magic". Mirascope allows the user to write the messages array manually, which has the added benefit of accessing functionality that is not yet supported by the template parser (such as Vision support).

```python
from mirascope import BasePrompt
from openai.types.chat import ChatCompletionMessageParam


class ImageDetection(BasePrompt):

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
