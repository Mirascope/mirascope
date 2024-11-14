---
title: Understanding LangChain Runnables
description: >
  Learn about LangChain runnables, how they work, and when best to use them. We also contrast runnables with Mirascope's pythonic chaining techniques.
authors:
  - willbakst
categories:
  - Tips & Inspiration
date: 2024-07-10
slug: langchain-runnables
---

# Understanding LangChain Runnables

A LangChain runnable is a protocol that allows you to create and invoke custom chains. It’s designed to sequence tasks, taking the output of one call and feeding it as input to the next, making it suitable for straightforward, linear tasks where each step directly builds upon the previous one.

Runnables simplify the process of building, managing, and modifying complex workflows by providing a standardized way for different components to interact. With a single function call, you can execute a chain of operations — which is useful for scenarios where the same series of steps need to be applied multiple times.

<!-- more -->

A runnable consists of several parts. At a minimum, these include:

- **Methods:** these are the functions that a runnable can perform. The standard interface of a runnable includes methods like`invoke` , `batch` , `stream` , and their corresponding async methods (`ainvoke` , `abatch` , `astream`). These methods allow you to define custom chains and invoke them in a standard way.
- **Input and output schemas:** all runnables expose input and output schemas, allowing you to inspect and understand the input type a runnable expects and the output type it produces.
- **Components:** various components in LangChain implement the runnable interface, including (but not limited to) chat models, large language models (LLMs), output parsers, retrievers, [prompt templates](https://mirascope.com/blog/langchain-prompt-template), and more.

With runnables, you can easily combine components using the pipe (`|`) operator to build workflows for complex chains, which lets you link together prompts and function calls to architect complex flows — though at the cost of potential challenges in error handling, performance, and transparency.

One of the key characteristics of runnables is their ability to handle concurrency. The runnable interface includes `async` methods that can be used with [asyncio’s](https://docs.python.org/3/library/asyncio.html) `await` syntax for concurrency. This allows you to run multiple tasks concurrently, improving the efficiency and performance of your applications.

Moreover, if a component in a chain fails, the error will be propagated up the chain, making it easier to handle errors and exceptions, and implement fallbacks in a more consistent and predictable way.

While LangChain's **'runnable’** offers a great solution for creating and invoking custom chains — a functionality we appreciate — **runnables are another abstraction that LLM app developers have to learn**. And while the LangChain Expression Language (LCEL) works well for simple chains, they become increasingly complicated to work with as chains grow more complex.

That’s why we created [Mirascope](https://github.com/mirascope/mirascope), our Python toolkit for building with LLMs. It offers building blocks rather than a monolithic framework, and allows you to code as you normally would in Python without having to learn new abstractions.

In this article, we provide an overview of how a LangChain Runnable works, along with some of its pros and cons. Then, we contrast this with Mirascope’s approach to chaining.

## How Runnables Work in LangChain

In LangChain, a [runnable can be any Python callable](https://python.langchain.com/v0.1/docs/expression_language/interface/), such as a function, a lambda expression, or an instance method of a class. However, instead of directly passing these callables around, you wrap them in a runnable object to provide additional functionality and metadata, like the function name, execution time, or custom annotations.

Here's an example of how you can create a runnable from a function:

```python
from langchain_core.runnables import RunnableLambda


# Define a simple function
def greet(name):
   return f"Hello, {name}!"


# Wrap the function in a RunnableWrapper
greet_runnable = RunnableLambda(lambda x: greet(x))


# Use the runnable to call the function
result = greet_runnable.invoke("Alice")
print(result)  # Output: Hello, Alice!
```

In the above code, we defined a simple `greet` function that takes a name as an argument and returns a greeting string. This function is then wrapped in a `RunnableWrapper`.

`greet_runnable` provides additional functionality and metadata, making it easier to integrate with other parts of your code. This allows you to manage and pass around multiple callables with additional context or behavior.

One advantage of wrapping callables as runnables is you can now connect them using LangChain's chaining mechanisms, such as the pipe operator (`|`), the `RunnableSequence` class, or the `.pipe( )` method.

For example, you can use [`RunnableSequence`](https://api.python.langchain.com/en/latest/runnables/langchain_core.runnables.base.RunnableSequence.html) to create a chain applying multiple transformations to some input data: ‍

```python
from datetime import datetime

from langchain_core.runnables import RunnableLambda, RunnableSequence


# Define the transformations as simple functions
def greet(name):
   return f"Hello, {name}!"


def append_datetime(text):
   current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   return f"{text} The current date and time is {current_datetime}."


def to_uppercase(text):
   return text.upper()


def add_exclamation(text):
   return f"{text}!"


# Wrap the functions in RunnableWrapper
greet_runnable = RunnableLambda(lambda x: greet(x))
datetime_runnable = RunnableLambda(lambda x: append_datetime(x))
uppercase_runnable = RunnableLambda(lambda x: to_uppercase(x))
exclamation_runnable = RunnableLambda(lambda x: add_exclamation(x))


# Create a RunnableSequence with the wrapped runnables
chain = RunnableSequence(
   first=greet_runnable,
   middle=[datetime_runnable, uppercase_runnable],
   last=exclamation_runnable,
)


# Apply the chain to some input data
input_data = "Alice"
result = chain.invoke(input_data)
print(
   result
)  # Output example: "HELLO, ALICE! THE CURRENT DATE AND TIME IS 2024-06-19 14:30:00!"
```

Here we have four simple functions: `greet` , `append_datetime` , `to_uppercase` , and `add_exclamation` , each of which takes input and performs a specific transformation on it. `RunnableLambda` takes a function as its argument, and creates a runnable object.

We can then create a `RunnableSequence` by passing these runnables to its constructor:

```python
chain = RunnableSequence(
   first=greet_runnable,
   middle=[datetime_runnable, uppercase_runnable],
   last=exclamation_runnable,
)
```

`RunnableSequence` executes these runnables in sequential order, using the output of one runnable as input to the next.

The result of a chain is a `RunnableSequence` which is still a runnable that can still be piped, invoked, streamed, etc.

### Creating A Runnable with the Chain Decorator

The `@chain` decorator allows you to turn any function into a chain. Below, the decorator creates a custom chain that combines multiple components, such as [prompts](https://mirascope.com/blog/prompt-engineering-tools), models, and output parsers, and defines a function (`custom_chain`) that encapsulates the sequence of operations:

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import chain
from langchain_openai import ChatOpenAI

prompt1 = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
prompt2 = ChatPromptTemplate.from_template("What is the subject of this joke: {joke}")

@chain
def custom_chain(text):
    prompt_val1 = prompt1.invoke({"topic": text})
    output1 = ChatOpenAI().invoke(prompt_val1)
    parsed_output1 = StrOutputParser().invoke(output1)
    chain2 = prompt2 | ChatOpenAI() | StrOutputParser()
    return chain2.invoke({"joke": parsed_output1})
custom_chain.invoke("bears")
# Output: 'The subject of this joke is bears.'
```

### `invoke`, `batch`, and `stream` Methods

As previously mentioned, LangChain runnables provide three key methods to execute and interact with your chains:

- `invoke`: executes a runnable with a single input, and\*\*\*\* is typically used when you have a single piece of data to process.
- `batch`: allows you to process multiple inputs in parallel. This method is useful when you have a list of inputs and want to run them through the chain simultaneously.
  ‍
- `stream`: processes input data as a stream, handling one piece of data at a time and providing results as they are available. This method is ideal for handling streamed output for real-time data processing or for large datasets that you want to process incrementally. At the time of this writing, streaming support for retries is being added for higher reliability without any latency cost (as explained in their docs).

### Key Runnable Types in LangChain

Within LangChain, you have access to various runnable types that allow you to execute and manage tasks:

- `RunnableParallel` for parallelizing operations.
- `RunnablePassthrough` for passing data unchanged from previous steps for use as input in later steps.
- `RunnableLambda` for converting a Python callable into a runnable.

### `RunnableParallel`

This runs a mapping of runnables in parallel and returns a mapping of their outputs. It’s essentially a dictionary whose values are runnables, and it invokes them concurrently, providing the same input to each.

A [`RunnableParallel`](https://python.langchain.com/v0.1/docs/expression_language/primitives/parallel/) can be instantiated directly or by using a dictionary literal within a sequence. This is particularly useful when you want to parallelize operations or manipulate the output of one runnable to match the input format of the next runnable in a sequence.

Below is an example that uses functions to illustrate how `RunnableParallel` works.

```python
import asyncio

from langchain_core.runnables import RunnableLambda


def add_one(x: int) -> int:
   return x + 1


def mul_two(x: int) -> int:
   return x * 2


def mul_three(x: int) -> int:
   return x * 3


runnable_1 = RunnableLambda(add_one)
runnable_2 = RunnableLambda(mul_two)
runnable_3 = RunnableLambda(mul_three)


sequence = runnable_1 | {  # this dict is coerced to a RunnableParallel
   "mul_two": runnable_2,
   "mul_three": runnable_3,
}
# Or equivalently:
# sequence = runnable_1 | RunnableParallel(
#     {"mul_two": runnable_2, "mul_three": runnable_3}
# )
# Also equivalently:
# sequence = runnable_1 | RunnableParallel(
#     mul_two=runnable_2,
#     mul_three=runnable_3,
# )


print(sequence.invoke(1))
# > {'mul_two': 4, 'mul_three': 6}
print(sequence.batch([1, 2, 3]))
# > [{'mul_two': 4, 'mul_three': 6}, {'mul_two': 6, 'mul_three': 9}, {'mul_two': 8, 'mul_three': 12}]


async def async_invoke(sequence, x):
   return await sequence.ainvoke(x)


async def async_batch(sequence, x):
   return await sequence.abatch(x)


print(asyncio.run(async_invoke(sequence, 1)))
# > {'mul_two': 4, 'mul_three': 6}
print(asyncio.run(async_batch(sequence, [1, 2, 3])))
# > [{'mul_two': 4, 'mul_three': 6}, {'mul_two': 6, 'mul_three': 9}, {'mul_two': 8, 'mul_three': 12}]
```

### `RunnablePassthrough`

This is a [runnable](https://python.langchain.com/v0.1/docs/expression_language/primitives/passthrough/) that passes inputs through unchanged or with additional keys. It behaves almost like the identity function, except that it can be configured to add additional keys to the output, if the input is a dictionary.

It’s often used in conjunction with `RunnableParallel` to pass data through to a new key in the map, which allows you to keep the original input intact while adding some extra information.

```python
# !pip install -qU langchain langchain-openai

import os

from langchain_core.runnables import RunnableParallel, RunnablePassthrough

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

runnable = RunnableParallel(
    passed=RunnablePassthrough(),
    modified=lambda x: x["num"] + 1,
)

runnable.invoke({"num": 1})
# Output: {'passed': {'num': 1}, 'modified': 2}
```

Here, the `passed` key was called with `RunnablePassthrough`, passing on the input data `{'num': 1}` without changes. And, the modified key was set using a lambda that added 1 to `num`, resulting in `modified` having the value `2`.

### `RunnableLambda`

[`RunnableLambda`](https://api.python.langchain.com/en/latest/runnables/langchain_core.runnables.base.RunnableLambda.html) is a LangChain abstraction that allows Python-callable functions to be transformed into functions compatible with LangChain's pipeline operations.

Wrapping a callable in a `RunnableLambda` makes the callable usable within either a `sync` or `async` context and can be composed as any other runnable. ‍

```python
# This is a RunnableLambda
from langchain_core.runnables import RunnableLambda

def add_one(x: int) -> int:
    return x + 1

runnable = RunnableLambda(add_one)

runnable.invoke(1) # returns 2
runnable.batch([1, 2, 3]) # returns [2, 3, 4]

# Async is supported by default by delegating to the sync implementation
await runnable.ainvoke(1) # returns 2
await runnable.abatch([1, 2, 3]) # returns [2, 3, 4]


# Alternatively, can provide both synd and sync implementations
async def add_one_async(x: int) -> int:
    return x + 1

runnable = RunnableLambda(add_one, afunc=add_one_async)
runnable.invoke(1) # Uses add_one
await runnable.ainvoke(1) # Uses add_one_async
```

As shown above, the code handles individual values and batches of data, using the provided `sync` and `async` implementations.

## Chaining with Mirascope

[Mirascope](https://mirascope.com) dispenses with abstractions like runnables and offers two ways of chaining: computed fields and function arguments.

### Chaining with Computed Fields

An example of chaining using Python's native functionality is shown below, where `explain_book` first calls `recommend_book` once and injects the result into the prompt template as a computed field:

```python
from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template(
   """
   Recommend a popular book in the {genre} genre.
   Give me just the title.
   """
)
def recommend_book(genre: str): ...


@openai.call("gpt-4o-mini")
@prompt_template(
   """
   SYSTEM:
   You are the world's greatest librarian.
   Your task is to explain why the book "{book_title}" is popular in the {genre} genre.

   USER:
   Explain why "{book_title}" in the {genre} genre is popular.
   """
)
def explain_book(genre: str) -> openai.OpenAIDynamicConfig:
   return {"computed_fields": {"book_title": recommend_book(genre)}}


explanation = explain_book("science fiction")
print(explanation)

# > "Dune," written by Frank Herbert, has garnered immense popularity in the science fiction genre...
```

Additionally, `computed_fields` includes the output at every step of the chain in the final dump:

```python
print(explanation.model_dump())
# {
#   "metadata": {},
#   "response": {
#     "id": "chatcmpl-ANYSOekHdvVOVKTUziTvDzCtCrbB4",
#     "choices": [
#       {
#         "finish_reason": "stop",
#         "index": 0,
#         "logprobs": null,
#         "message": {
#           "content": "\"Dune,\" written by Frank Herbert and first published in 1965, is considered a cornerstone of the science fiction genre for several compelling reasons:\n\n1. **Complex World-Building**: Herbert created an intricate universe with detailed geography, politics, religion, and ecology. The desert planet of Arrakis (Dune) is not merely a backdrop, but a living ecosystem that plays a crucial role in the story. The depth of this world-building allows readers to immerse themselves fully in the narrative.\n\n2. **Themes of Power and Politics**: \"Dune\" delves into themes of imperialism, feudalism, and the struggle for power. It explores how individuals and groups navigate political machinations, often with profound consequences. These themes resonate with readers as they reflect real-world issues of governance, control, and rebellion.\n\n3. **Ecological and Environmental Awareness**: The book introduces the idea of the environment\u2019s fragility, particularly through the significance of the spice melange, which is vital for space travel and has profound effects on the human mind. It raises awareness about ecological balance and the exploitation of natural resources, themes that are increasingly relevant in today\u2019s context of climate change and environmental degradation.\n\n4. **Fascination with Mysticism and Religion**: Herbert infused the narrative with elements of mysticism and religious symbolism, particularly through the character of Paul Atreides, who embodies the potential for messianic and prophetic power. This adds layers of philosophical inquiry about destiny, belief, and the nature of knowledge.\n\n5. **Rich Characterization and Development**: The characters in \"Dune\" are multifaceted and undergo significant development, making them relatable and memorable. Paul's journey from heir to a noble family to a powerful leader is complex, and readers are drawn into his internal conflicts and growth.\n\n6. **Cultural Impact**: \"Dune\" has influenced numerous other works in literature, film, and games. Its themes, motifs, and characters have become archetypes within the genre. Adaptations, such as David Lynch's 1984 film and Denis Villeneuve's 2021 adaptation, have further renewed interest and engagement with the original text.\n\n7. **Innovative Concepts**: The book introduces groundbreaking ideas, such as the concept of a human mind augmenting through the spice and the intricate workings of the Bene Gesserit sisterhood. These innovative concepts challenge the status quo of science fiction and push the boundaries of imagination.\n\n8. **Longevity and Nuance**: \"Dune\" continues to be relevant and compelling across generations. It invites diverse interpretations and discussions, offering new insights on every read. Its sophistication and richness allow for deep exploration of its themes, keeping it alive in academic discussions.\n\nOverall, \"Dune\" is popular not just for its compelling narrative and characters, but also for its deep engagement with significant and timeless themes, making it a rich text that continues to inspire and influence readers and creators in the science fiction genre.",
#           "refusal": null,
#           "role": "assistant",
#           "audio": null,
#           "function_call": null,
#           "tool_calls": null
#         }
#       }
#     ],
#     "created": 1730177360,
#     "model": "gpt-4o-mini-2024-07-18",
#     "object": "chat.completion",
#     "service_tier": null,
#     "system_fingerprint": "fp_f59a81427f",
#     "usage": {
#       "completion_tokens": 600,
#       "prompt_tokens": 52,
#       "total_tokens": 652,
#       "completion_tokens_details": {
#         "audio_tokens": null,
#         "reasoning_tokens": 0
#       },
#       "prompt_tokens_details": {
#         "audio_tokens": null,
#         "cached_tokens": 0
#       }
#     }
#   },
#   "tool_types": null,
#   "prompt_template": "\n   SYSTEM:\n   You are the world's greatest librarian.\n   Your task is to explain why the book \"{book_title}\" is popular in the {genre} genre.\n\n\n   USER:\n   Explain why \"{book_title}\" in the {genre} genre is popular.\n   ",
#   "fn_args": {
#     "genre": "science fiction",
#     "book_title": {
#       "metadata": {},
#       "response": {
#         "id": "chatcmpl-ANYSNPhRVQlMRuEUiwMeL07Z44k3f",
#         "choices": [
#           {
#             "finish_reason": "stop",
#             "index": 0,
#             "logprobs": null,
#             "message": {
#               "content": "Dune",
#               "refusal": null,
#               "role": "assistant",
#               "audio": null,
#               "function_call": null,
#               "tool_calls": null
#             }
#           }
#         ],
#         "created": 1730177359,
#         "model": "gpt-4o-mini-2024-07-18",
#         "object": "chat.completion",
#         "service_tier": null,
#         "system_fingerprint": "fp_f59a81427f",
#         "usage": {
#           "completion_tokens": 2,
#           "prompt_tokens": 23,
#           "total_tokens": 25,
#           "completion_tokens_details": {
#             "audio_tokens": null,
#             "reasoning_tokens": 0
#           },
#           "prompt_tokens_details": {
#             "audio_tokens": null,
#             "cached_tokens": 0
#           }
#         }
#       },
#       "tool_types": null,
#       "prompt_template": "\n   Recommend a popular book in the {genre} genre.\n   Give me just the title.\n   ",
#       "fn_args": {
#         "genre": "science fiction"
#       },
#       "dynamic_config": null,
#       "messages": [
#         {
#           "role": "user",
#           "content": "Recommend a popular book in the science fiction genre.\nGive me just the title."
#         }
#       ],
#       "call_params": {},
#       "call_kwargs": {
#         "model": "gpt-4o-mini",
#         "messages": [
#           {
#             "role": "user",
#             "content": "Recommend a popular book in the science fiction genre.\nGive me just the title."
#           }
#         ]
#       },
#       "user_message_param": {
#         "content": "Recommend a popular book in the science fiction genre.\nGive me just the title.",
#         "role": "user"
#       },
#       "start_time": 1730177359100.959,
#       "end_time": 1730177359672.126,
#       "message_param": {
#         "content": "Dune",
#         "refusal": null,
#         "role": "assistant",
#         "tool_calls": null
#       },
#       "tools": null,
#       "tool": null,
#       "audio": null,
#       "audio_transcript": null
#     }
#   },
#   "dynamic_config": {
#     "computed_fields": {
#       "book_title": {
#         "metadata": {},
#         "response": {
#           "id": "chatcmpl-ANYSNPhRVQlMRuEUiwMeL07Z44k3f",
#           "choices": [
#             {
#               "finish_reason": "stop",
#               "index": 0,
#               "logprobs": null,
#               "message": {
#                 "content": "Dune",
#                 "refusal": null,
#                 "role": "assistant",
#                 "audio": null,
#                 "function_call": null,
#                 "tool_calls": null
#               }
#             }
#           ],
#           "created": 1730177359,
#           "model": "gpt-4o-mini-2024-07-18",
#           "object": "chat.completion",
#           "service_tier": null,
#           "system_fingerprint": "fp_f59a81427f",
#           "usage": {
#             "completion_tokens": 2,
#             "prompt_tokens": 23,
#             "total_tokens": 25,
#             "completion_tokens_details": {
#               "audio_tokens": null,
#               "reasoning_tokens": 0
#             },
#             "prompt_tokens_details": {
#               "audio_tokens": null,
#               "cached_tokens": 0
#             }
#           }
#         },
#         "tool_types": null,
#         "prompt_template": "\n   Recommend a popular book in the {genre} genre.\n   Give me just the title.\n   ",
#         "fn_args": {
#           "genre": "science fiction"
#         },
#         "dynamic_config": null,
#         "messages": [
#           {
#             "role": "user",
#             "content": "Recommend a popular book in the science fiction genre.\nGive me just the title."
#           }
#         ],
#         "call_params": {},
#         "call_kwargs": {
#           "model": "gpt-4o-mini",
#           "messages": [
#             {
#               "role": "user",
#               "content": "Recommend a popular book in the science fiction genre.\nGive me just the title."
#             }
#           ]
#         },
#         "user_message_param": {
#           "content": "Recommend a popular book in the science fiction genre.\nGive me just the title.",
#           "role": "user"
#         },
#         "start_time": 1730177359100.959,
#         "end_time": 1730177359672.126,
#         "message_param": {
#           "content": "Dune",
#           "refusal": null,
#           "role": "assistant",
#           "tool_calls": null
#         },
#         "tools": null,
#         "tool": null,
#         "audio": null,
#         "audio_transcript": null
#       }
#     }
#   },
#   "messages": [
#     {
#       "role": "system",
#       "content": "You are the world's greatest librarian.\nYour task is to explain why the book \"Dune\" is popular in the science fiction genre."
#     },
#     {
#       "role": "user",
#       "content": "Explain why \"Dune\" in the science fiction genre is popular."
#     }
#   ],
#   "call_params": {},
#   "call_kwargs": {
#     "model": "gpt-4o-mini",
#     "messages": [
#       {
#         "role": "system",
#         "content": "You are the world's greatest librarian.\nYour task is to explain why the book \"Dune\" is popular in the science fiction genre."
#       },
#       {
#         "role": "user",
#         "content": "Explain why \"Dune\" in the science fiction genre is popular."
#       }
#     ]
#   },
#   "user_message_param": {
#     "content": "Explain why \"Dune\" in the science fiction genre is popular.",
#     "role": "user"
#   },
#   "start_time": 1730177359689.837,
#   "end_time": 1730177366119.564,
#   "message_param": {
#     "content": "\"Dune,\" written by Frank Herbert and first published in 1965, is considered a cornerstone of the science fiction genre for several compelling reasons:\n\n1. **Complex World-Building**: Herbert created an intricate universe with detailed geography, politics, religion, and ecology. The desert planet of Arrakis (Dune) is not merely a backdrop, but a living ecosystem that plays a crucial role in the story. The depth of this world-building allows readers to immerse themselves fully in the narrative.\n\n2. **Themes of Power and Politics**: \"Dune\" delves into themes of imperialism, feudalism, and the struggle for power. It explores how individuals and groups navigate political machinations, often with profound consequences. These themes resonate with readers as they reflect real-world issues of governance, control, and rebellion.\n\n3. **Ecological and Environmental Awareness**: The book introduces the idea of the environment\u2019s fragility, particularly through the significance of the spice melange, which is vital for space travel and has profound effects on the human mind. It raises awareness about ecological balance and the exploitation of natural resources, themes that are increasingly relevant in today\u2019s context of climate change and environmental degradation.\n\n4. **Fascination with Mysticism and Religion**: Herbert infused the narrative with elements of mysticism and religious symbolism, particularly through the character of Paul Atreides, who embodies the potential for messianic and prophetic power. This adds layers of philosophical inquiry about destiny, belief, and the nature of knowledge.\n\n5. **Rich Characterization and Development**: The characters in \"Dune\" are multifaceted and undergo significant development, making them relatable and memorable. Paul's journey from heir to a noble family to a powerful leader is complex, and readers are drawn into his internal conflicts and growth.\n\n6. **Cultural Impact**: \"Dune\" has influenced numerous other works in literature, film, and games. Its themes, motifs, and characters have become archetypes within the genre. Adaptations, such as David Lynch's 1984 film and Denis Villeneuve's 2021 adaptation, have further renewed interest and engagement with the original text.\n\n7. **Innovative Concepts**: The book introduces groundbreaking ideas, such as the concept of a human mind augmenting through the spice and the intricate workings of the Bene Gesserit sisterhood. These innovative concepts challenge the status quo of science fiction and push the boundaries of imagination.\n\n8. **Longevity and Nuance**: \"Dune\" continues to be relevant and compelling across generations. It invites diverse interpretations and discussions, offering new insights on every read. Its sophistication and richness allow for deep exploration of its themes, keeping it alive in academic discussions.\n\nOverall, \"Dune\" is popular not just for its compelling narrative and characters, but also for its deep engagement with significant and timeless themes, making it a rich text that continues to inspire and influence readers and creators in the science fiction genre.",
#     "refusal": null,
#     "role": "assistant",
#     "tool_calls": null
#   },
#   "tools": null,
#   "tool": null,
#   "audio": null,
#   "audio_transcript": null
# }
```

We generally recommend [chaining with computed fields](https://mirascope.com/blog/prompt-chaining) for a variety of use cases because it takes advantage of dynamic configuration and you’re able to cache and reuse outputs as needed. Even when using shorthand or messages syntax for writing prompts, we recommend returning both `messages` and `computed_fields` in a dynamic config so the computed fields still propagate.

### Chaining with Functions Arguments

You can alternatively chain components together by explicitly passing the output of one function as input into the next function in the chain:

```python
from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template(
   """
   Recommend a popular book in the {genre} genre.
   Give me just the title.
   """
)
def recommend_book(genre: str): ...


@openai.call("gpt-4o-mini")
@prompt_template(
   """
   SYSTEM:
   You are the world's greatest librarian.
   Your task is to explain why the book "{book_title}" is popular in the {genre} genre.

   USER:
   Explain why "{book_title}" in the {genre} genre is popular.
   """
)
def explain_book(genre: str, book_title: str): ...


genre = "science fiction"


def explain_book_chain(genre: str):
   book_title = recommend_book(genre)
   explanation = explain_book(genre, book_title.content)
   print(explanation.content)


explain_book_chain("science fiction")
# > "Dune," a science fiction novel by Frank Herbert, is popular because...
```

While functions offer a straightforward way to chain, they lack the ability to colocate all inputs and outputs along the chain within one prompt function.

On the other hand, functions offer explicit control over execution flow, and complex chains with conditional or dynamic steps can be simpler to implement compared to properties.

Also, functions use standard Python logic so they’re easy to understand and reuse across different parts of your code. This flexibility is particularly useful when applying the same chaining logic in various contexts or with different classes.

## Key Differentiators: Langchain’s Runnable vs Mirascope’s Pythonic Chaining

[LangChain's approach](https://mirascope.com/blog/llamaindex-vs-langchain) relies on specialized abstractions like LCEL and the Runnable class. These aim to provide a declarative and expressive way to compose chains, but they also introduce an additional layer of complexity that developers must learn and navigate.

Simple chains in LangChain are indeed clean and somewhat easy to use, but for chains that are more complex because you need to pass arguments through them at runtime, constructs like `RunnablePassthrough` might be necessary.

Such abstractions often require additional learning and debugging, and can be [harder to understand](https://mirascope.com/blog/langchain-alternatives), especially for developers more accustomed to working with plain Python.

In contrast, Mirascope allows you to build and chain components using familiar pythonic syntax and inheritance, which can minimize the learning curve and maintain code readability.

## Build LLM Applications Using the Python You Already Know

Mirascope doesn’t impose unnecessary abstractions or steep learning curves, and allows you to implement chaining with clean, pythonic logic. It also promotes true prompt engineering best practices like colocation and [version control](https://mirascope.com/blog/prompt-versioning), so you can focus on your core task of building LLM applications for many different use cases like chatbots and RAG (retrieval augmentation generation).

‍Want to learn more? You can find more Mirascope code samples on both our [documentation site](https://mirascope.com) and on [GitHub](https://github.com/mirascope/mirascope/).
