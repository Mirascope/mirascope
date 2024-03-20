<div align="center" justiry="start">
    <a href="https://www.mirascope.io">
        <img align="bottom" src="https://github.com/Mirascope/mirascope/assets/99370834/e403d7ee-f8bc-4df1-b2d0-33763f021c89" alt="Frog Logo" width="84"/><br><img align="bottom" src="https://uploads-ssl.webflow.com/65a6fd6a1c3b2704d6217d3d/65b5674e9ceef563dc57eb11_Medium%20length%20hero%20headline%20goes%20here.svg" width="400" alt="Mirascope"/>
    </a>
</div>

<p align="center">
    <a href="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml" target="_blank"><img src="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml/badge.svg?branch=main" alt="Tests"/></a>
    <a href="https://codecov.io/github/Mirascope/mirascope" target="_blank"><img src="https://codecov.io/github/Mirascope/mirascope/graph/badge.svg?token=HAEAWT3KC9" alt="Coverage"/></a>
    <a href="https://docs.mirascope.io/" target="_blank"><img src="https://img.shields.io/badge/docs-available-brightgreen" alt="Docs"/></a>
    <a href="https://pypi.python.org/pypi/mirascope" target="_blank"><img src="https://img.shields.io/pypi/v/mirascope.svg" alt="PyPI Version"/></a>
    <a href="https://pypi.python.org/pypi/mirascope" target="_blank"><img src="https://img.shields.io/pypi/pyversions/mirascope.svg" alt="Stars"/></a>
    <a href="https://github.com/Mirascope/mirascope/stargazers" target="_blank"><img src="https://img.shields.io/github/stars/Mirascope/mirascope.svg" alt="Stars"/></a>
</p>

---

**Mirascope** is an LLM toolkit for lightning-fast, high-quality development. Building with Mirascope feels like writing the Python code you’re already used to writing.

## Installation

```bash
pip install mirascope
```

You can also install additional optional dependencies if you’re using those features:

```bash
pip install mirascope[anthropic]  # AnthropicCall, ...
pip install mirascope[gemini]     # GeminiCall, ...
pip install mirascope[wandb]      # WandbOpenAICall, ...
pip install mirascope[all]        # all optional dependencies
```

## Examples

### Colocation

Colocation is the core of our philosophy. Everything that can impact the quality of a call to an LLM — from the prompt to the model to the temperature — must live together so that we can properly version and test the quality of our calls over time. This is useful since we have all of the information including metadata that we could want for analysis, which is particularly important during rapid development.

```python
import os

from mirascope import tags
from mirascope.openai import OpenAICall, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


@tags(["version:0003"])
class Editor(OpenAICall):
    prompt_template = """
    SYSTEM:
    You are a top class manga editor.
    
    USER:
    I'm working on a new storyline. What do you think?
    {storyline}
    """
    
    storyline: str
    
    call_params = OpenAICallParams(model="gpt-4", temperature=0.4)


storyline = "..."
editor = Editor(storyline=storyline)

print(editor.messages())
# > [{'role': 'system', 'content': 'You are a top class manga editor.'}, {'role': 'user', 'content': "I'm working on a new storyline. What do you think?\n..."}]

critique = editor.call()
print(critique.content)
# > I think the beginning starts off great, but...

print(editor.dump() | critique.dump())
# {
#     "tags": ["version:0003"],
#     "template": "SYSTEM:\nYou are a top class manga editor.\n\nUSER:\nI'm working on a new storyline. What do you think?\n{storyline}",
#     "inputs": {"storyline": "..."},
#     "start_time": 1710452778501.079,
#     "end_time": 1710452779736.8418,
#     "output": {
#         "id": "chatcmpl-92nBykcXyTpxwAbTEM5BOKp99fVmv",
#         "choices": [
#             {
#                 "finish_reason": "stop",
#                 "index": 0,
#                 "logprobs": None,
#                 "message": {
#                     "content": "I think the beginning starts off great, but...",
#                     "role": "assistant",
#                     "function_call": None,
#                     "tool_calls": None,
#                 },
#             }
#         ],
#         "created": 1710452778,
#         "model": "gpt-4-0613",
#         "object": "chat.completion",
#         "system_fingerprint": None,
#         "usage": {"completion_tokens": 25, "prompt_tokens": 33, "total_tokens": 58},
#     },
# }
```

### Chat History

Our template parser makes inserting chat history beyond easy:

```python
from openai.types.chat import ChatCompletionMessageParam

from mirascope.openai import OpenAICall


class Librarian(OpenAICall):
    prompt_template = """
    SYSTEM: You are the world's greatest librarian.
    MESSAGES: {history}
    USER: {question}
    """

    question: str
    history: list[ChatCompletionMessageParam] = []


librarian = Librarian(question="", history=[])
while True:
    librarian.question = input("(User): ")
    response = librarian.call()
    librarian.history += [
        {"role": "user", "content": librarian.question},
        {"role": "assistant", "content": response.content},
    ]
    print(f"(Assistant): {response.content}")

#> (User): What fantasy book should I read?
#> (Assistant): Have you read the Name of the Wind?
#> (User): I have! What do you like about it?
#> (Assistant): I love the intricate world-building...
```

### Tools (Function Calling)

We’ve made implementing and using tools (function calling) intuitive:

```python
from typing import Literal

from mirascope.openai import OpenAICall, OpenAICallParams


def get_current_weather(
    location: str, unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
):
    """Get the current weather in a given location."""
    if "tokyo" in location.lower():
        print(f"It is 10 degrees {unit} in Tokyo, Japan")
    elif "san francisco" in location.lower():
        print(f"It is 72 degrees {unit} in San Francisco, CA")
    elif "paris" in location.lower():
        print(f"It is 22 degress {unit} in Paris, France")
    else:
        print("I'm not sure what the weather is like in {location}")


class Forecast(OpenAICall):
    prompt_template = "What's the weather in Tokyo?"

    call_params = OpenAICallParams(model="gpt-4", tools=[get_current_weather])

tool = Forecast().call().tool
if tool:
    tool.fn(**tool.args)
	  #> It is 10 degrees fahrenheit in Tokyo, Japan
```

### Chaining

Chaining multiple calls together for Chain of Thought (CoT) is as simple as writing a function:

```python
import os
from functools import cached_property

from mirascope.openai import OpenAICall, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class ChefSelector(OpenAICall):
    prompt_template = "Name a chef who is really good at cooking {food_type} food"

    food_type: str

    call_params = OpenAICallParams(model="gpt-3.5-turbo-0125")


class RecipeRecommender(ChefSelector):
    prompt_template = """
    SYSTEM:
    Imagine that you are chef {chef}.
    Your task is to recommend recipes that you, {chef}, would be excited to serve.

    USER:
    Recommend a {food_type} recipe using {ingredient}.
    """

    ingredient: str
    
    call_params = OpenAICallParams(model="gpt-4")

    @cached_property  # !!! so multiple access doesn't make multiple calls
    def chef(self) -> str:
        """Uses `ChefSelector` to select the chef based on the food type."""
        return ChefSelector(food_type=self.food_type).call().content

response = RecipeRecommender(food_type="japanese", ingredient="apples").call()
print(response.content)
# > Certainly! Here's a recipe for a delicious and refreshing Japanese Apple Salad: ...
```

### Extracting Structured Information

Convenience built on top of tools that makes extracting structured information reliable:

```python
from typing import Literal, Type

from mirascope.openai import OpenAIExtractor
from pydantic import BaseModel


class TaskDetails(BaseModel):
    description: str
    due_date: str
    priority: Literal["low", "normal", "high"]


class TaskExtractor(OpenAIExtractor[TaskDetails]):
    extract_schema: Type[TaskDetails] = TaskDetails
    prompt_template = """
    Extract the task details from the following task:
    {task}
    """

    task: str


task = "Submit quarterly report by next Friday. Task is high priority."
task_details = TaskExtractor(task=task).extract()
assert isinstance(task_details, TaskDetails)
print(TaskDetails)
#> description='Submit quarterly report' due_date='next Friday' priority='high'
```

### FastAPI Integration

Since we’ve built our `BasePrompt` on top of [Pydantic](https://pydantic.dev/), we integrate with tools like [FastAPI](https://fastapi.tiangolo.com/) out-of-the-box:

```python
import os
from typing import Type

from fastapi import FastAPI
from mirascope.openai import OpenAIExtractor
from pydantic import BaseModel

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

app = FastAPI()


class Book(BaseModel):
    title: str
    author: str


class BookRecommender(OpenAIExtractor[Book]):
    extract_schema: Type[Book] = Book
    prompt_template = "Please recommend a {genre} book."

    genre: str


@app.post("/")
def root(book_recommender: BookRecommender) -> Book:
    """Generates a book based on provided `genre`."""
    return book_recommender.extract()
```

## Roadmap

- [x]  Extracting structured information using LLMs
- [ ]  Streaming extraction for tools (function calling)
- [ ]  Additional template parsing for more complex messages
    - [x]  Chat History
    - [ ]  Additional Metadata
    - [ ]  Vision
- [ ]  RAG
- [ ]  Agents
- [ ]  Support for more LLM providers:
    - [X]  Anthropic Function Calling
    - [ ]  Mistral
    - [ ]  HuggingFace
- [ ]  Integrations
    - [x]  Weights & Biases
    - [x]  LangChain / LangSmith
    - [ ]  … tell us what you’d like integrated!
- [ ]  Evaluating prompts and their quality by version

## Versioning

Mirascope uses [Semantic Versioning](https://semver.org/).

## License

This project is licensed under the terms of the [MIT License](https://github.com/Mirascope/mirascope/blob/main/LICENSE).
