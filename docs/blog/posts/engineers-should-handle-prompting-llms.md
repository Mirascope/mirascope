---
title: Engineers Should Handle Prompting LLMs (and Prompts Should Live in Your Codebase)
description: >
  Many prompt engineering tools neither follow developer best practices, nor manage prompts with their LLM calls. We created Mirascope to address this.
authors:
  - willbakst
categories:
  - Tips & Inspiration
date: 2024-03-29
slug: engineers-should-handle-prompting-llms
---

# Engineers Should Handle Prompting LLMs (and Prompts Should Live in Your Codebase)

We’ve seen many discussions around Large Language Model (LLM) software development allude to a workflow where prompts live apart from LLM calls and are managed by multiple stakeholders, including non-engineers. In fact, many popular LLM development frameworks and libraries are built in a way that _requires_ prompts to be managed separately from their calls.

We think this is an unnecessarily cumbersome approach that’s not scalable for complex, production-grade LLM software development.

Here’s why: for anyone developing production-grade LLM apps, prompts that include code will necessarily be a part of your engineering workflow. Therefore, separating prompts from the rest of your codebase, especially from their API calls, means you’re splitting that workflow into different, independent parts.

Separating concerns and assigning different roles to manage each may _seem_ to bring certain efficiencies, for example, easing collaboration between tech and non-tech roles. But **it introduces fundamental complexity that can disrupt the engineering process.** For instance, introducing a change in one place—like adding a new key-value pair to an input for an LLM call—means hunting down that change manually. And then, you will likely _still_ not catch all the errors.

<!-- more -->

Don’t get us wrong. If your prompts are purely text or have very minimal code, then managing them separately from your calls may not have much of an impact. And there are legitimate examples of prompts with minimal or no code, like prompts for ChatGPT. In such cases, managing prompts separately from calls can make sense.

But any enterprise-grade LLM apps require sophisticated prompts, **which means you’ll end up writing code for such prompts anyway.**

In fact, **trying to write out that logic in text would be even more complicated.** In our view, code makes prompting both efficient and manageable, as well as the purview of engineers.

Below, we outline how we arrived at this truth, and how the solution we’ve developed (a Python-based LLM development library) helps developers manage prompts in the codebase easily and efficiently, making, in our experience, LLM app development faster and more enjoyable.

## Our Frustrations with Developer Tools for Prompt Engineering

Our view on prompting started as we were using an early version of the OpenAI SDK to build out interpretable machine learning tools at a previous company. This was the standard OpenAI API for accessing GPT model functionalities.

Back then we didn’t have the benefit of any useful helper libraries, so we wrote all the API code ourselves. This amounted to writing lots of boilerplate to accomplish what seemed like simple tasks. For example, automatically extracting the model configuration (such as constraints) from just the name of the features in a given dataset. This required many prompt iterations and it was a pain to evaluate them.

It was around that time that we began asking ourselves: why aren’t there better [developer tools in the prompt engineering
space](https://mirascope.com/blog/prompt-engineering-tools)? Is it because people are bringing experimental stuff into production too quickly? Or simply because the space is so new?

The more we worked to develop our LLM applications, the more it was clear that from a software engineer's perspective, the **separation of prompt management from the calls was fundamentally flawed.** It made the actual engineering slow, cumbersome and arguably more error prone. It was almost as if current tools weren't built around developer best practices but rather around Jupyter notebook best practices (if there even is such a thing).

Beyond that, we noticed some other issues:

- Our prompts became unmanageable past two versions. We weren’t using a prompt management workflow back then, so implementing changes was a manual process. We started telling colleagues not to touch the code because it might break a function somewhere else.
- A lot of libraries tried to offer functionality for as many use cases as possible, sometimes making you feel dependent on them. They required you to do things their way, or you’d have to wait for them to catch up with new features from the LLMs.

All this led us to rethink how prompts should be managed to make developers’ lives easier. In the end, these frustrations boiled over into us wanting to build our own library that approached LLM development in a developer-first way to make LLM app development faster and more enjoyable. This ultimately became [Mirascope](https://github.com/mirascope/mirascope).

## How Mirascope Makes Prompt Engineering Intuitive and Scalable

For us, prompt engineering boils down to the relationship between the prompt and the API call. Mirascope represents what we feel is a best-in-class approach for generating that prompt, taking the LLM response, and tracking all aspects of that flow.

As developers, we want to focus on innovation and creativity, rather than on managing and troubleshooting underlying processes.

To that end, we designed Mirascope with the following features and capabilities to make your prompting more efficient, simpler, and scalable.

### Code Like You Already Code, with Pythonic Simplicity

It was important to us to be able to just code in Python, without having to learn superfluous abstractions or extra, fancy structures that make development more cumbersome than it needs to be. So we designed Mirascope to do just that.

For instance, we don’t make you implement directed acyclic graphs in the context of sequencing function calls. We provide code that’s eminently readable, lightweight, and maintainable.

An example of this is our [`prompt_template`](https://mirascope.com/learn/prompts/#prompt-templates-messages) decorator, which encapsulates as much logic within the prompt as feasible.

Within a decorated function, the return value can be used as the prompt template. The following example requests book recommendations based on particular genre:

```python
from mirascope.core import prompt_template


@prompt_template()
def book_recommendation_prompt(genre: str) -> str:
    return f"Recommend a {genre} book"


prompt = book_recommendation_prompt("fantasy")
print(prompt)
# > [BaseMessageParam(role='user', content='Recommend a fantasy book')]
```

You can also provide a string template directly as an argument of the decorator where the function arguments will be injected into the template automatically:

```python
from mirascope.core import prompt_template


@prompt_template("Recommend a {genre} book")
def book_recommendation_prompt(genre: str): ...


prompt = book_recommendation_prompt("fantasy")
print(prompt)
# > [BaseMessageParam(role='user', content='Recommend a fantasy book')]
```

By default, Mirascope's `prompt_template` treats the prompt message as a single user message in order to simplify initial use and implementation for straightforward scenarios.

But you may want to add more context to prompts in the form of different roles, such as system, user, or assistant roles to generate more nuanced responses, as shown here:

```python
from mirascope.core import Messages, prompt_template


@prompt_template()
def book_recommendation_prompt(genre: str) -> Messages.Type:
    return [
        Messages.System("You are a librarian"),
        Messages.User(f"Recommend a {genre} book"),
    ]


prompt = book_recommendation_prompt("fantasy")
print(prompt)
# > [
#     BaseMessageParam(role='system', content='You are a librarian'),
#     BaseMessageParam(role='user', content='Recommend a fantasy book'),
#   ]
```

Now running this prompt template will automatically parse and structure the prompt as a list of `BaseMessageParam` message objects that work across all supported providers.

You can also use all caps keywords in a string template for the same functionality:

```python
from mirascope.core import prompt_template


@prompt_template(
    """
    SYSTEM: You are a librarian
    USER: Recommend a {genre} book
    """
)
def book_recommendation_prompt(genre: str): ...


prompt = book_recommendation_prompt("fantasy")
print(prompt)
# > [
#     BaseMessageParam(role='system', content='You are a librarian'),
#     BaseMessageParam(role='user', content='Recommend a fantasy book'),
#   ]
```

We also provide decorators for turning prompt templates into actual calls to an LLM API. This further reduces the boilerplate needed to write LLM-powered functions:

```python
from mirascope.core import openai


@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)
# > Sure! I'd be happy to recommend...
```

In the above example, we've directly decorated the function, which means the function is now tied to a specific provider. As before, you can always instead use the `prompt_template` decorator to write provider-agnostic prompts, which you can then use with the decorator for any supported provider:

```python
from mirascope.core import prompt_template


@prompt_template(
    """
    SYSTEM: You are a librarian
    USER: Recommend a {genre} book
    """
)
def book_recommendation_prompt(genre: str): ...


# OpenAI call and response
openai_recommend_book = openai.call(
    "gpt-4o-mini",
)(book_recommendation_prompt)
openai_response = openai_recommend_book("fantasy")
print(openai_response.content)

# Anthropic call and response
anthropic_recommend_book = anthropic.call(
    "claude-3-5-sonnet-20240620",
)(book_recommendation_prompt)
anthropic_response = anthropic_recommend_book("fantasy")
print(anthropic_response.content)
```

Writing prompts this way enables endless possibilities and customization, from few-shot prompting to chat interactions with an LLM and so much more.

We also wanted to avoid introducing complexity where it's not absolutely necessary. For example, given a choice in how we would chain together components, we'd prefer relying on native Python rather than relying on something like the pipe moderator.

The goal is to maintain an interface that remains as Pythonic as possible.

**Note** : This isn’t to say there’s one “best” way to accomplish chaining, and you're certainly not required to do it exactly as we've shown. For instance, you can also have two separate calls where you pass the output of the first into the second as an argument (rather than calling it inside of the first call). It's not our recommendation since it breaks colocation, but you're free to do what you like. We just have opinionated guidelines, not requirements.

Nevertheless, this approach to chaining encapsulates each step of the process within class methods, allowing for a clean and readable way to sequentially execute tasks that depend on the outcome of previous steps:

```python
from mirascope.core import Messages, openai


@openai.call("gpt-4o-mini")
def select_chef(food_type: str) -> str:
    return f"Name a chef who is good at cooking {food_type} food"


@openai.call("gpt-4o-mini")
def recommend_recipe(ingredient: str, food_type: str) -> str:
    chef = select_chef(food_type)
    return "Imagine you are {chef}. Recommend a {food_type} recipe using {ingredient}"


response = recommend_recipe("apples", "japanese")
print(response.content)
# > Certainly! Here's a delightful Japanese-inspired recipe using apples: ...
```

Finally, we show an example of how you can use Mirascope to do few-shot prompting, which provides the language model with a few examples (shots) to help it understand the task and generate better output.

Below are three example sets of book recommendations for different topics to guide the model in understanding the format and type of response expected when asked to recommend books on a new topic, such as "coding."

```python
from mirascope.core import prompt_template


@prompt_template(
    """
    I'm looking for book recommendations on various topics. Here are some examples:

    1. For a topic on 'space exploration', you might recommend:
        - 'The Right Stuff' by Tom Wolfe
        - 'Cosmos' by Carl Sagan

    2. For a topic on 'artificial intelligence', you might recommend:
        - 'Life 3.0' by Max Tegmark
        - 'Superintelligence' by Nick Bostrom

    3. For a topic on 'historical fiction', you might recommend:
        - 'The Pillars of the Earth' by Ken Follett
        - 'Wolf Hall' by Hilary Mantel

    Can you recommend some books on {topic}?
    """
)
def few_shot_book_recommendation_prompt(topic: str): ...
```

Minimizing complexity lowers the learning curve. In Mirascope’s case, beyond knowing our library and Python, the only framework to learn is Pydantic for structuring and validating outputs.

### Built-in Data Validation for Error-Free Prompting

We find that high-quality prompts—ones that are type and error checked—lead to more accurate and useful LLM responses, and so data validation is at the heart of what we do.

Automatic validation against predefined schemas is built into the fabric of our framework, allowing you to be more productive rather than having to chase down bugs or code your own basic error handling logic.

For starters, by writing prompts as typed functions, you can easily ensure valid and well-formed inputs for you prompts by using Pydantic's [`validate_call`](https://docs.pydantic.dev/latest/concepts/validation_decorator/) decorator. We've also written our `BaseCallResponse` class as an extension of Pydantic's [`BaseModel`](https://docs.pydantic.dev/latest/api/base_model/), and we've implemented first-class support for structuring LLM outputs as BaseModel instances as well.

All of this means:

- Mirascope prompt templates can easily ensure the data is correctly typed before it's processed and sent over to the API, leading to cleaner, more maintainable code. Developers can focus more on the business logic specific to prompting rather than on writing boilerplate.
- Pydantic easily serializes data both to and from JSON format, which simplifies the process of dumping and saving LLM responses (without any additional tooling).
- Everything is engineered with editor support in mind, offering autocomplete and proper type hints.
- It also lets developers define custom validation methods if needed, allowing them to enforce complex rules that go beyond type checks and basic validations.

An example of using Pydantic for enforcing type validation (with graceful error handling) is shown below:

```python
from pydantic import BaseModel, ValidationError
from mirascope.core import openai


class Book(BaseModel):
    title: str
    author: str


@openai.call("gpt-4o-mini", response_model=Book)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


try:
    book = recommend_book("fantasy")
    assert isinstance(book, Book)
    print(book)
except ValidationError as e:
    print(e)
    # > 1 validation error for Book
    #  price
    #    Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='standard', input_type=str]
    #      For further information visit      https://errors.pydantic.dev/2.6/v/float_parsing
```

You can also validate data in ways that are difficult if not impossible to code successfully, but that LLMs excel at, such as analyzing sentiment. For instance, you can add Pydantic’s [`AfterValidator`](https://mirascope.com/learn/response_models/#validation-and-error-handling) annotation to Mirascope’s extracted output as shown below:

```python
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ValidationError
from mirascope.core import openai


@openai.call("gpt-4o-mini", response_model=Literal["happy", "sad"])
def classify_sentiment(text: str) -> str:
    return f"Is the following text happy or sad? {text}"


def validate_happy(story: str) -> str:
    """Confirm that the story is happy."""
    assert classify_sentiment(story) == "happy", "Story wasn't happy"
    return story


@openai.call(
    model="gpt-4o-mini",
    response_model=Annotated[str, AfterValidator(validate_happy)],
)
def tell_sad_story() -> str:
    return "Tell me a very sad story."


try:
    story = tell_sad_story()
    print(story)
except ValidationError as e:
    print(e)
    # > 1 validation error for Story
    #   story
    #     Assertion failed, Story wasn't happy. [type=assertion_error, input_value="Once upon a time, there ...er every waking moment.", input_type=str]
    #       For further information visit https://errors.pydantic.dev/2.6/v/assertion_error
```

### Simplify LLM Interactions with Decorators and Integrations

We believe in freeing you from writing boilerplate to interact with APIs, we we made available a number of arguments for easily modifying and customizing how you use the underlying APIs.

For example, you can set `stream=True` in the function decorator, which will generate a stream of chunks (and tools, which will be `None` if not using tools):

```python
from mirascope.core import openai


@openai.call("gpt-4o-mini", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


for chunk, _ in recommend_book("fantasy"):
    print(chunk.content, end="", flush=True)
```

You can also further configure the API call by setting the `call_params` argument, meaning that any time the decorated function is called it will use the correct, colocated call parameters:

```python
from mirascope.core import openai


@openai.call("gpt-4o-mini", call_params={"temperature": 0.7})
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)
```

If a provider has a custom endpoint you can call with their own API (for example, OpenAI compatibility), you can set the `client` argument in the decorator to use the custom client. This is true for providers such as [Ollama](https://ollama.com/), [Anyscale](https://www.anyscale.com/), [Together](https://www.together.ai/), [AzureOpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service), and others that support the OpenAI API through a proxy (as well as any other APIs such as Anthropic that have similar support).

```python
from mirascope.core import openai
from openai import OpenAI


client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required, but unused
)


@openai.call("gpt-4o-mini", client=client)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)
```

We also made sure that Mirascope works well with or integrates directly with tools such as Logfire, OpenTelemetry, HyperDX, Langfuse, and more for easily tracking machine learning experiments and visualizing data as well as improving prompt effectiveness through automated refinement and testing. All together these tools work together with Mirascope as [an alternative to LangChain](https://mirascope.com/blog/langchain-alternatives).

Beyond OpenAI, Mirascope supports currently these [other LLM providers](https://mirascope.com/learn/calls):

- Anthropic
- Mistral
- Google Gemini
- Groq
- Cohere
- LiteLLM
- Azure AI
- AWS Bedrock

We've made sure that every example in our documentation shows how to use each provider for easy copy-paste to try it out yourself.

We consistently add support for new providers, so if there is a provider you want to see supported that isn't yet, let us know!

If you want to switch to another model provider (like [Anthropic](https://mirascope.com/api/core/anthropic/call/) or [Mistral](https://mirascope.com/api/core/mistral/call/), for instance), you just need to change the decorator and the corresponding call parameters:

```python
from mirascope.core import anthropic


@anthropic.call("claude-3-5-sonnet-20240620")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)
```

### Expand LLM Capabilities with Tools

Although LLMs are known mostly for text generation, you can provide them with specific tools (also known as [function calling](https://mirascope.com/learn/tools)) to extend their capabilities.

Examples of what you can do with tools include:

- Granting access to the Bing API or DuckDuckGo Search API for internet search to fetch the latest information on various topics.
- Providing a secure sandbox environment like Repl.it for dynamically running code snippets provided by users in a coding tutorial platform.
- Allowing access to the Google Cloud Natural Language API for evaluating customer feedback and reviews to determine sentiment and help businesses quickly identify areas for improvement.
- Providing a Machine Learning (ML) recommendation engine API for giving personalized content or product recommendations for an e-commerce website, based on natural language interactions with users.

Mirascope lets you easily [define tools](https://mirascope.com/learn/tools/#basic-usage-and-syntax) by documenting any function using a docstring as shown below. It automatically converts this into a tool, saving you additional work.

```python
from typing import Literal

from mirascope.core import openai, prompt_template


def get_current_weather(
    location: str, unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
):
    """Get the current weather in a given location."""
    if "tokyo" in location.lower():
        print(f"It is 10 degrees {unit} in Tokyo, Japan")
    elif "san francisco" in location.lower():
        print(f"It is 72 degrees {unit} in San Francisco, CA")
    elif "paris" in location.lower():
        print(f"It is 22 degrees {unit} in Paris, France")
    else:
        print("I'm not sure what the weather is like in {location}")


@openai.call(model="gpt-4o", tools=[get_current_weather])
def forecast(city: str) -> str:
    return f"What's the weather in {city}?"


response = forecast("Tokyo")
if tool := response.tool:
    tool.call()
```

Mirascope supports Google, ReST, Numpydoc, and Epydoc style docstrings for creating tools. If a particular function doesn’t have a docstring, you can define your own `BaseTool` class. You can then define the `call()` method to attach the docstring-less function’s functionality to the tool, but use your own custom docstrings:

```python
from mirascope.core import BaseTool


# has no docstings
def get_weather(city: str) -> str: ...


class GetWeather(BaseTool):
    """Gets the weather in a city."""

    city: str

    def call(self) -> str:
        return get_weather(self.city)
```

Tools allow you to dynamically generate prompts based on current or user-specified data such as extracting current weather data in a given city before generating a prompt like, "Given the current weather conditions in Tokyo, what are fun outdoor activities?"

See our [documentation](https://mirascope.com/learn/tools) for details on generating prompts in this way (for instance, by calling the `call` method).

### Extract Structured Data from LLM-Generated Text

LLMs are great at producing conversations in text, which is unstructured information. But many applications need structured data from LLM outputs. Scenarios include:

- Extracting structured information from a PDF invoice (i.e., invoice number, vendor, total charges, taxes, etc.) so that you can automatically insert that information into another system like a CRM or tracking tool, a spreadsheet, etc.
- Automatically extracting sentiment, feedback categories (product quality, service, delivery, etc.), and customer intentions from customer reviews or survey responses.
- Pulling out specific medical data such as symptoms, diagnoses, medication names, dosages, and patient history from clinical notes.
- Extracting financial metrics, stock data, company performance indicators, and market trends from financial reports and news articles.

To handle such scenarios, we support extraction with the [`response_model`](https://mirascope.com/learn/response_models) argument in the decorator, which leverages tools (or optionally `json_mode=True`) to reliably extract structured data from the outputs of LLMs according to the schema defined in a Pydantic `BaseModel`. In the example below you can see how due dates, priorities, and descriptions are being extracted:

```python
from typing import Literal

from mirascope.core import openai, prompt_template
from pydantic import BaseModel, Field


class TaskDetails(BaseModel):
    due_date: str = Field(...)
    priority: Literal["low", "normal", "high"] = Field(...)
    description: str = Field(...)


@openai.call(
    model="gpt-4o",
    response_model=TaskDetails,
    call_params={"tool_choice": "required"},
)
def get_task_details(task: str) -> str:
    return f"Extract the details from the following task: {task}"


task = "Submit quarterly report by next Friday. Task is high priority."
task_details = get_task_details(task)
assert isinstance(task_details, TaskDetails)
print(task_details)
# > due_date='next Friday' priority='high' description='Submit quarterly report'
```

You can define schema parameters against which to extract data in Pydantic’s `BaseModel` class, by setting certain attributes and fields in that class. Mirascope also lets you set the number of retries to extract data in case a failure occurs. But you also don’t have to use a detailed schema like `BaseModel` if you’re [extracting built-in types](https://mirascope.com/learn/response_models/#built-in-types) like strings, integers, booleans, etc. The code sample below shows how extraction for a simple structure like a list of strings doesn’t need a full-fledged schema definition.

```python
from mirascope.core import openai


@openai.call(model="gpt-4o", response_model=list[str])
def recommend_books(genre: str) -> str:
    return f"Recommend 3 {genre} books"


books = recommend_books(genre="fantasy")
print(books)
# > [
#   'The Name of the Wind by Patrick Rothfuss',
#   'Mistborn: The Final Empire by Brandon Sanderson',
#   'The Way of Kings by Brandon Sanderson'
#   ]
```

Mirascope makes things as simple as feasible, requiring you to write less code in cases where more code isn't necessary.

### Facilitate Your Prompt Workflows with CLI and IDE Support

As mentioned earlier, our experience with prompts is that they generally become unmanageable after a certain number of iterations. Versioning is obviously a good idea, and we see some cloud prompting tools that offer this, but as they don’t generally colocate prompts with LLM calls, not all the relevant information gets versioned, unfortunately.

We believe it’s important to colocate as much information with the prompt as feasible, and that it should all be versioned together as a single unit. It's also extremely important that this versioning happens automatically and captures the entire lexical closure (so that changes to dependent functions can be easily identified through the automatic versioning).

Our prompt engineering framework [Lilypad](https://lilypad.so/docs) lets you:

- Write prompts and LLM functions like you normally would
- Automatically versions any change to the function
- Automatically traces every call to the function against its version
- Is fully open-source and can be used locally

This ensures that you can engineer your prompts as part of your standard Git workflow without having to worry about manually tracking minor changes during development. Colleagues can also see everything that was tried as well as the differences between prompts.

When installed, Lilypad creates a predefined directory structure as shown below:

```plaintext
|
|-- .lilypad/
|-- |-- config.json
|-- lily/
|   |-- __init__.py
|   |-- {llm_function_name}.py
|-- pad.db
```

This creates a prompt management environment that supports collaboration and allows you to centralize prompt development in one place. LLM functions live in the `lily` folder, and automatic versions and traces live in the `pad.db` SQLite database.

By versioning the entire lexical closure and tracing every call automatically, you can continue iterating on your prompts and any other code in your codebase without having to worry about manually tracking the potential impacts of such changes on the outputs of your functions.

If you want to give Mirascope a try, we recommend taking a look at our [documentation](https://mirascope.com). You can also find our source code on [GitHub](https://github.com/mirascope/mirascope). Don't forget to give us a star!
