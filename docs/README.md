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

**Mirascope** is an intuitive approach to building with LLMs. Building with Mirascope feels like writing the Python code you’re already used to writing.

## Installation

```bash
pip install mirascope
```

You can also install additional optional dependencies if you’re using those features:

```bash
pip install mirascope[anthropic]  # AnthropicCall, ...
pip install mirascope[groq]       # GroqCall, ...
pip install mirascope[logfire]    # with_logfire decorator, ...
pip install mirascope[all]        # all optional dependencies
```

> Note: escape brackets (e.g. `pip install mirascope\[anthropic\]`) if using zsh

## Getting Started

<div align="center">
    <a href="https://www.youtube.com/watch?v=P44M_IC4YyY"><img src="./assets/overview-screenshot-with-play-button.png" alt="Overview" width="340"></a>
	<a href="https://www.youtube.com/watch?v=uGobZSm2P4Q"><img src="./assets/quickstart-screenshot-with-play-button.png" alt="QuickStart" width="340"></a>
</div>

## Examples

### Colocation

[Colocation](./concepts/philosophy.md#4-colocation) is one of the core tenets of our philosophy. Everything that can impact the quality of a call to an LLM — from the prompt to the model to the temperature — must live together so that we can properly version and test the quality of our calls over time. This is useful since we have all of the information including metadata that we could want for analysis, which is particularly important during rapid development.

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

print(editor.messages()) # white-space is automatically stripped
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

Our template parser makes inserting [chat history](./concepts/chat_history.md) beyond easy:

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

We’ve made implementing and using [tools (function calling)](./concepts/tools_(function_calling).md) intuitive:

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
        print(f"I'm not sure what the weather is like in {location}")


class Forecast(OpenAICall):
    prompt_template = "What's the weather in Tokyo?"

    call_params = OpenAICallParams(model="gpt-4", tools=[get_current_weather])

tool = Forecast().call().tool
if tool:
    tool.fn(**tool.args)
	  #> It is 10 degrees fahrenheit in Tokyo, Japan
```

### Chaining

[Chaining](./concepts/chaining_calls.md) multiple calls together is as simple as writing a property:

```python
import os
from functools import cached_property

from mirascope.openai import OpenAICall
from pydantic import computed_field

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class ChefSelector(OpenAICall):
    prompt_template = """
    Name a chef who is really good at cooking {food_type} food.
    Give me just the name.
    """

    food_type: str


class RecipeRecommender(ChefSelector):
    prompt_template = """
    SYSTEM:
    Imagine that you are chef {chef}.
    Your task is to recommend recipes that you, {chef}, would be excited to serve.

    USER:
    Recommend a recipe using {ingredient}.
    """

    ingredient: str

    @computed_field
    @cached_property
    def chef(self) -> str:
        """Uses `ChefSelector` to select the chef based on the food type."""
        return ChefSelector(food_type=self.food_type).call().content


recommender = RecipeRecommender(food_type="japanese", ingredient="apples")
recipe = recommender.call()
print(recipe.content)
# > Certainly! Here's a recipe for a delicious and refreshing Japanese Apple Salad: ...
```

Of course, you can also chain calls together in sequence rather than through properties and wrap the chain in a function for reusability. You can find an example of this [here](./concepts/chaining_calls.md#chaining-directly-function-chaining).

### Extracting Structured Information

Convenience built on top of tools that makes [extracting structured information](./concepts/extracting_structured_information_using_llms.md) reliable:

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
print(task_details)
#> description='Submit quarterly report' due_date='next Friday' priority='high'
```

### FastAPI Integration

Since we’ve built our `BasePrompt` on top of [Pydantic](https://pydantic.dev/), we [integrate](./integrations/fastapi.md) with tools like [FastAPI](https://fastapi.tiangolo.com/) out-of-the-box:

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

## Supported Providers and Integrations

You can find a list of [supported providers](./concepts/supported_llm_providers.md) with examples of how to use them with Mirascope.

We are constantly working to further integrate Mirascope as seamlessly as possible with as many tools as possible. You can find the [integrations that we currently support](./integrations/client_wrappers.md) in our docs. If there are any integrations that you want, let us know!

## Roadmap

- [ ]  Agents
    - [X]  Easy tool calling and execution
    - [ ]  More convenience around TOOL messages
    - [ ]  Base classes for ReAct agents
    - [ ]  Base classes for Query Planning agents
    - [ ]  Tons of examples...
- [ ]  RAG
    - [X]  ChromaDB
    - [X]  Pinecone
    - [X]  OpenAI Embeddings
    - [X]  Cohere Embeddings
    - [ ]  Hugging Face
    - [ ]  Tons of examples...
- [ ] Mirascope CLI
    - [X] Versioning prompts / calls / extractors
    - [ ] RAG CLI (e.g. versioning stores, one-off vector store interactions)
    - [ ] Versioning integrations with LLMOps tools (e.g. Weave, LangSmith, ...)
    - [ ] LLM Provider Auto-conversion
    - [ ] Templates (`mirascope from_template pinecone_rag_openai_call my_call_name`)
- [X]  Extracting structured information using LLMs
- [X]  Streaming extraction for tools (function calling)
- [ ]  Additional template parsing for more complex messages
    - [X]  Chat History
    - [X]  List + List[List] Convenience
    - [ ]  Additional Metadata
    - [ ]  Vision
- [ ]  Support for more LLM providers:
    - [X]  Anthropic
    - [X]  Cohere
    - [X]  Mistral
    - [X]  Groq
    - [X]  Gemini
    - [ ]  HuggingFace
- [ ]  Integrations
    - [X]  Logfire by Pydantic
    - [X]  Langfuse
    - [X]  Weights & Biases Trace
    - [X]  Weave by Weights & Biases
    - [X]  LangChain / LangSmith
    - [ ]  … tell us what you’d like integrated!
- [ ]  Evaluating prompts and their quality by version

## Versioning

Mirascope uses [Semantic Versioning](https://semver.org/).

## License

This project is licensed under the terms of the [MIT License](https://github.com/Mirascope/mirascope/blob/main/LICENSE).
