<p align="center">
    <a href="https://www.mirascope.io"><img src="https://uploads-ssl.webflow.com/65a6fd6a1c3b2704d6217d3d/65b5674e9ceef563dc57eb11_Medium%20length%20hero%20headline%20goes%20here.svg" width="400" alt="Mirascope"/></a>
</p>

<p align="center">
    <strong><em>Prompt Engineering focused on:</em></strong>
</p>

<div align="center">
    <table>
        <tr>
            <td align="center" width="420"><em>Simplicity through idiomatic syntax</em></td>
            <td align="center">→</td>
            <td align="center" width="420"><strong><em>Faster and more reliable releases</em></strong></td>
        </tr>
        <tr>
            <td align="center" width="420"><em>Semi-opinionated methods</em></td>
            <td align="center">→</td>
            <td align="center" width="420"><strong><em>Reduced complexity that speeds up development</em></strong></td>
        </tr>
        <tr>
            <td align="center" width="420"><em>Reliability through validation</em></td>
            <td align="center">→</td>
            <td align="center" width="420"><strong><em>More robust applications with fewer bugs</em></strong></td>
        </tr>
        <tr>
            <td align="center" width="420"><em>High-quality up-to-date documentation</em></td>
            <td align="center">→</td>
            <td align="center" width="420"><strong><em>Trust and reliability</em></strong></td>
        </tr>
    </table>
</div>

<p align="center">
    <a href="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml" target="_blank"><img src="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml/badge.svg?branch=main" alt="Tests"/></a>
    <a href="https://docs.mirascope.io/" target="_blank"><img src="https://img.shields.io/badge/docs-available-brightgreen" alt="Docs"/></a>
    <a href="https://pypi.python.org/pypi/mirascope" target="_blank"><img src="https://img.shields.io/pypi/v/mirascope.svg" alt="PyPI Version"/></a>
    <a href="https://pypi.python.org/pypi/mirascope" target="_blank"><img src="https://img.shields.io/pypi/pyversions/mirascope.svg" alt="Stars"/></a>
    <a href="https://github.com/Mirascope/mirascope/stargazers" target="_blank"><img src="https://img.shields.io/github/stars/Mirascope/mirascope.svg" alt="Stars"/></a>
</p>

---

**Documentation**: <a href="https://docs.mirascope.io" target="_blank">https://docs.mirascope.io</a>

**Source Code**: <a href="https://github.com/Mirascope/mirascope" target="_blank">https://github.com/Mirascope/mirascope</a>

---

**Mirascope** is a library purpose-built for Prompt Engineering on top of <a href="https://pydantic.dev" target="_blank">Pydantic 2.0</a>:

- Prompts can live as self-contained classes in their own directory:

```python
# prompts/book_recommendation.py
from mirascope import Prompt


class BookRecommendationPrompt(Prompt):
    """
    I've recently read the following books: {titles_in_quotes}.
    
    What should I read next?
    """

    book_titles: list[str]

    @property
    def titles_in_quotes(self) -> str:
        """Returns a comma separated list of book titles each in quotes."""
        return ", ".join([f'"{title}"' for title in self.book_titles])
```

- Use the prompt anywhere without worrying about internals such as formatting:

```python
# script.py
from prompts import BookRecommendationPrompt

prompt = BookRecommendationPrompt(
    book_titles=["The Name of the Wind", "The Lord of the Rings"]
)

print(str(prompt))
#> I've recently read the following books: "The Name of the Wind", "The Lord of the Rings".
#  What should I read next?

print(prompt.messages)
#> [('user', 'I\'ve recently read the following books: "The Name of the Wind", "The Lord of the Rings".\nWhat should I read next?')]
```

## Why use Mirascope?

* **Intuitive**: Editor support that you expect (e.g. **autocompletion**, **inline errors**)
* **Peace of Mind**: Pydantic together with our Prompt CLI **eliminate prompt-related bugs**.
* **Durable**: Seamlessly customize and extend functionality. **Never maintain a fork**.
* **Integration**: Easily integrate with **JSON Schema** and other tools such as **FastAPI**
* **Convenience**: Tooling that is **clean**, **elegant**, and **delightful** that **you don't need to maintain**.
* **Open**: Dedication to building **open-source tools** you can use with **your choice of LLM**.

## Requirements

**Pydantic** is the only strict requirement, which will be included automatically during installation.

The Prompt CLI and LLM Convenience Wrappers have additional requirements, which you can opt-in to include if you're using those features.

## Installation

Install Mirascope and start building with LLMs in minutes.

```sh
$ pip install mirascope
```

This will install the `mirascope` package along with `pydantic`.

To include extra dependencies, run:

```sh
$ pip install mirascope[cli]     #  Prompt CLI
$ pip install mirascope[openai]  #  LLM Convenience Wrappers
$ pip install mirascope[all]     #  All Extras
```

<details>
<summary>For those using zsh, you'll need to escape brackets:</summary>

```sh
$ pip install mirascope\[all\]
```

</details>

## 🚨 Warning: Strong Opinion 🚨

Prompt Engineering is engineering. Beyond basic illustrative examples, prompting quickly becomes complex. Separating prompts from the engineering workflow will only put limitations on what you can build with LLMs. We firmly believe that prompts are far more than "just f-strings" and thus require developer tools that are purpose-built for building these more complex prompts as easily as possible.

## Examples

The `Prompt` class is an extension of [`BaseModel`](https://docs.pydantic.dev/latest/api/base_model/) with some additional built-in convenience tooling for writing and formatting your prompts:

```python
from mirascope import Prompt

class GreetingsPrompt(Prompt):
    """
    Hello! It's nice to meet you. My name is {name}. How are you today?
    """

    name: str

prompt = GreetingsPrompt(name="William Bakst")

print(GreetingsPrompt.template())
#> Hello! It's nice to meet you. My name is {name}. How are you today?

print(prompt)
#> Hello! It's nice to meet you. My name is William Bakst. How are you today?
```

<details>
<summary>Example of <strong>autocomplete</strong> and <strong>inline errors</strong>:</summary>
<ul>
    <li>Autocomplete:</li>
    <img width="822" alt="Screenshot 2024-01-30 at 7 10 11 PM" src="https://github.com/Mirascope/mirascope/assets/99370834/812a97c1-7f0d-472c-842d-305d7f5da085">
    <li>Inline Errors:</li>
    <img width="571" alt="Screenshot 2024-01-30 at 7 08 54 PM" src="https://github.com/Mirascope/mirascope/assets/99370834/e09466a0-0941-46ec-abdb-e55cf84f1f25">
</ul>
</details>

You can access the docstring prompt template through the `GreetingsPrompt.template()` class method, which will automatically take care of removing any additional special characters such as newlines. This enables writing longer prompts that still adhere to the style of your codebase:

```python
class GreetingsPrompt(Prompt):
    """
    Salutations! It is a lovely day. Wouldn't you agree? I find that lovely days
    such as these brighten up my mood quite a bit. I'm rambling...

    My name is {name}. It's great to meet you.
    """

prompt = GreetingsPrompt(name="William Bakst")
print(prompt)
#> Salutations, good being! It is a lovely day. Wouldn't you agree? I find that lovely days such as these brighten up my mood quite a bit. I'm rambling...
#> My name is William Bakst. It's great to meet you.
```

The `str` method is written such that it only formats properties that are templated. This enables writing more complex properties that rely on one or more provided properties:

```python
class GreetingsPrompt(Prompt):
    """
    Hi! My name is {formatted_name}. {name_specific_remark}

    What's your name? Is your name also {name_specific_question}?
    """

    name: str

    @property
    def formatted_name(self) -> str:
        """Returns `name` with pizzazz."""
        return f"⭐{self.name}⭐"

    @property
    def name_specific_question(self) -> str:
        """Returns a question based on `name`."""
        if self.name == self.name[::-1]:
            return "a palindrome"
        else:
            return "not a palindrome"

    @property
    def name_specific_remark(self) -> str:
        """Returns a remark based on `name`."""
        return f"Can you believe my name is {self.name_specific_question}"

prompt = GreetingsPrompt(name="Bob")
print(prompt)
#> Hi! My name is ⭐Bob⭐. Can you believe my name is a palindrome?
#> What's your name? Is your name also a palindrome?
```

Notice that writing properties in this way ensures prompt-specific logic is tied directly to the prompt. It happens under the hood from the perspective of the person using `GreetingsPrompt` class. Constructing the prompt only requires `name`.

For writing promps with multiple messages with different roles, you can use the `messages` decorator to extend the functionality of the `messages` property:

```python
from mirascope import Prompt, messages

@messages
class GreetingsPrompt(Prompt):
    """
    SYSTEM:
    You can only speak in haikus.

    USER:
    Hello! It's nice to meet you. My name is {name}. How are you today?
    """

    name: str

prompt = GreetingsPrompt(name="William Bakst")

print(GreetingsPrompt.template())
#> SYSTEM: You can only speak in haikus.
#> USER: Hello! It's nice to meet you. My name is {name}. How are you today?

print(prompt)
#> SYSTEM: You can only speak in haikus.
#> USER: Hello! It's nice to meet you. My name is William Bakst. How are you today?

print(prompt.messages)
#> [('system', 'You can only speak in haikus.'), ('user', "Hello! It's nice to meet you. My name is William Bakst. How are you today?")]
```

The base `Prompt` class without the decorator will still have the `messages` attribute, but it will return a single user message in the list.

<details>
<summary>Remember: this is python</summary>
<p>There's nothing stopping you from doing things however you'd like. For example, reclaim the docstring:</p>

```python
from mirascope import Prompt

TEMPLATE = """
This is now my prompt template for {topic}
"""

class NormalDocstringPrompt(Prompt):
    """This is now just a normal docstring."""

    topic: str

    def template(self) -> str:
        """Returns this prompt's template."""
        return TEMPLATE

prompt = NormalDocstringPrompt(topic="prompts")
print(prompt)
#> This is now my prompt template for prompt
```

<p>Since the `Prompt`'s `str` method uses template, the above will work as expected.</p>
</details>

Because the `Prompt` class is built on top of `BaseModel`, prompts easily integrate with tools like [FastAPI](https://fastapi.tiangolo.com):

<details>
<summary>FastAPI Example</summary>

```python
from fastapi import FastAPI
from mirascope import OpenAIChat

from prompts import GreetingsPrompt

app = FastAPI()


@app.post("/greetings")
def root(prompt: GreetingsPrompt) -> str:
    """Returns an AI generated greeting."""
    model = OpenAIChat(api_key=os.environ["OPENAI_API_KEY"])
    return str(model.create(prompt))
```

</details>

You can also use the `Prompt` class with whichever LLM you want to use:

<details>
<summary>Mistral Example</summary>

```python
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from prompts import GreetingsPrompt

client = MistralClient(api_key=os.environ["MISTRAL_API_KEY"])

prompt = GreetingsPrompt(name="William Bakst")
messages = [
    ChatMessage(role=role, content=content)
    for role, content in prompt.messages
]

# No streaming
chat_response = client.chat(
    model="mistral-tiny",
    messages=messages,
)
```

</details>

<details>
<summary>OpenAI Example</summary>

```python
from openai import OpenAI

from prompts import GreetingsPrompt

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

prompt = GreetingsPrompt(name="William Bakst")
messages = [
    {"role": role, "content": content}
    for role, content in prompt.messages
]

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
)
```

</details>

## Dive Deeper

- Check out all of the possibilities of what you can do with [Pydantic Prompts](concepts/pydantic_prompts.md).
- Take a look at our [Mirascope CLI](concepts/mirascope_cli.md) for a semi-opinionated prompt mangement system.
- For convenience, we provide some wrappers around the OpenAI Python SDK for common tasks such as creation, streaming, tools, and extraction. We've found that the concepts covered in [LLM Convenience Wrappers](concepts/llm_convenience_wrappers.md) make building LLM-powered apps delightful.
- The [API Reference](api/prompts.md) contains full details on all classes, methods, functions, etc.
- You can take a look at [code examples](https://github.com/Mirascope/mirascope/tree/main/cookbook) in the repo that demonstrate how to use the library effectively.

## Contributing

Mirascope welcomes contributions from the community! See the [contribution guide](CONTRIBUTING.md) for more information on the development workflow. For bugs and feature requests, visit our [GitHub Issues](https://github.com/mirascope/mirascope/issues) and check out our [templates](https://github.com/Mirascope/mirascope/tree/main/.github/ISSUE_TEMPLATES).

## How To Help

Any and all help is greatly appreciated! Check out our page on [how you can help](HELP.md).

## Roadmap (What's on our mind)

- [X] Better DX for Mirascope CLI (e.g. autocomplete)
- [X] Functions as OpenAI tools
- [ ] Better chat history
- [ ] Testing for prompts
- [ ] Logging prompts and their responses
- [ ] Evaluating prompt quality
- [ ] RAG
- [ ] Agents


## Versioning

Mirascope uses [Semantic Versioning](https://semver.org/).

## License

This project is licensed under the terms of the [MIT License](https://github.com/Mirascope/mirascope/blob/main/LICENSE).
