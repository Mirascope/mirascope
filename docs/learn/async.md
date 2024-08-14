# Async

Asynchronous programming in Mirascope allows you to perform non-blocking operations, which can significantly improve the performance of your applications, especially when dealing with I/O-bound tasks like making API calls to Large Language Models (LLMs). This guide will walk you through how to use async features across various aspects of Mirascope.

## Basic Async Usage

To use async in Mirascope, you simply need to define your function as async and use the `await` keyword when calling it. Here's a basic example:

```python
import asyncio

from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str):
    ...


async def main():
    response = await recommend_book("fantasy")
    print(response.content)


asyncio.run(main())
```

In this example, the `recommend_book` function is defined as async, and we use `await` when calling it within another async function. You can handle asynchronous calls when using `response_model` or `output_parser` the exact same way.

## Async Streaming

Streaming with async works similarly to synchronous streaming, but you use `async for` instead of a regular `for` loop:

```python
import asyncio

from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini", stream=True)
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str):
    ...


async def main():
    stream = await recommend_book("fantasy")
    async for chunk, _ in stream:
        print(chunk.content, end="", flush=True)


asyncio.run(main())
```

## Async with Tools

When using tools asynchronously, you can make the `call` method of a tool async. Here's an example:

```python
import asyncio

from mirascope.core import openai, BaseTool, prompt_template


class FormatBook(BaseTool):
    title: str
    author: str

    async def call(self) -> str:
        # Simulating an async API call
        await asyncio.sleep(1)
        return f"{self.title} by {self.author}"


@openai.call(model="gpt-4o-mini", tools=[FormatBook])
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str):
    ...


async def main():
    response = await recommend_book("fantasy")
    if isinstance((tool := response.tool), FormatBook):
        output = await tool.call()
        print(output)
    else:
        print(response.content)


asyncio.run(main())
```

!!! tip "Type Hints"

    When using and calling asynchronous tools, you can check the type of the tool to get proper type hints.

## Async with BasePrompt

For `BasePrompt`, Mirascope provides a `run_async` method to access async functionality:

```python
import asyncio

from mirascope.core import BasePrompt, openai, prompt_template


@prompt_template("Analyze the sentiment of the following text: {text}")
class SentimentAnalysisPrompt(BasePrompt):
    text: str


async def main():
    prompt = SentimentAnalysisPrompt(text="I love using Mirascope!")
    result = await prompt.run_async(openai.call(model="gpt-4o-mini"))
    print(result.content)


asyncio.run(main())
```

## Parallel Async Calls

One of the main benefits of async is the ability to run multiple operations concurrently. Here's an example of making parallel async calls:

```python
import asyncio

from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini")
@prompt_template("Summarize the plot of a {genre} movie")
async def summarize_movie(genre: str): ...


async def main():
    genres = ["action", "comedy", "drama", "sci-fi"]
    tasks = [summarize_movie(genre) for genre in genres]
    results = await asyncio.gather(*tasks)

    for genre, result in zip(genres, results):
        print(f"{genre.capitalize()} movie summary:")
        print(result.content)
        print()


asyncio.run(main())
```

This example demonstrates how to use `asyncio.gather` to run multiple async calls concurrently, which can significantly reduce the total execution time compared to running them sequentially.

## Error Handling in Async Context

Error handling in async contexts is similar to synchronous code. You can use try/except blocks as usual:

```python
import asyncio

from mirascope.core import openai, prompt_template
from openai import APIError


@openai.call(model="gpt-4o-mini")
@prompt_template("Explain {concept} in simple terms")
async def explain_concept(concept: str):
    ...


async def main():
    try:
        response = await explain_concept("quantum computing")
        print(response.content)
    except APIError as e:
        print(f"An error occurred: {e}")


asyncio.run(main())
```

## Best Practices and Considerations

- **Use asyncio for I/O-bound tasks**: Async is most beneficial for I/O-bound operations like API calls. It may not provide significant benefits for CPU-bound tasks.
- **Avoid blocking operations**: Ensure that you're not using blocking operations within async functions, as this can negate the benefits of asynchronous programming.
- **Consider using connection pools**: When making many async requests, consider using connection pools to manage and reuse connections efficiently.
- **Be mindful of rate limits**: While async allows for concurrent requests, be aware of API rate limits and implement appropriate throttling if necessary.
- **Use appropriate timeouts**: Implement timeouts for async operations to prevent hanging in case of network issues or unresponsive services.
- **Test thoroughly**: Async code can introduce subtle bugs. Ensure comprehensive testing of your async implementations.
- **Leverage async context managers**: Use async context managers (async with) for managing resources that require setup and cleanup in async contexts.

By leveraging these async features in Mirascope, you can build more efficient and responsive applications, especially when working with multiple LLM calls or other I/O-bound operations.
