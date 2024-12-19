---
title: Mirascope V1 Release - Lessons Learned from Building an LLM Package
description: >
  Mirascope's stable release, V1 has been released. We discuss the reasons behind creating Mirascope and what led us to the changes from the original design to our V1 and what's coming down the road.
authors:
  - willbakst
categories:
  - Behind the Scenes
date: 2024-08-19
slug: mirascope-v1-release
---

# Mirascope V1 Release: Lessons Learned from Building an LLM Package

After months of development, countless iterations, and invaluable community feedback, we're excited to announce the release of Mirascope V1. This journey has been filled with challenges, insights, and breakthroughs. In this post, I'll share my experience building an LLM package, the design issues we encountered in V0, and how we've addressed them in V1.

<!-- more -->

## The Journey: Original Idea

We didn't actually intend to build a developer tool. We were working on a separate product and wanted to integrate LLMs into that product's workflow. Unfortunately everything was so new at the time that none of the existing developer tools fit our needs, so we started building our own internal tooling (which we've come to learn is the path many others have taken as well).

So we were building Mirascope out of necessity, and we felt that it would be best built out in the open as an open-source project considering how many others seemed to be feeling the same way.

Our goal with Mirascope was (and still is) to create a flexible, powerful tool for working with LLM APIs. We wanted to build a single layer abstraction on top of these APIs to improve their ergonomics without removing transparency or control. We wanted to build something provider-agnostic given how frequently a new "king" would pop up and be crowned the best LLM. We wanted to build something simple and elegant that felt like the natural progression from building with the base provider SDKs.

But most of all we wanted to build something Python-specific – something that properly took advantage of the qualities of Python that make it so loved.

We spent nearly 8 months building, testing, and refining our package in an open beta. Along the way, we learned a lot about LLM interactions, Python best practices, and the needs of the developer community.

## Design Challenges in V0

The initial version of Mirascope was developed as an internal tool, which meant that the problems we were solving were naturally specific to our use-case.

This led to several design challenges, which became particularly evident in more complex applications:

1. **Stateful Class-Based Approach** : Initially, we used a class-based system for LLM calls. While this seemed intuitive at first, it introduced unnecessary state and complexity. We realized that we had added state to the wrong parts of our abstractions.
2. **Performance Overhead** : Creating class instances for each LLM call resulted in performance overhead, especially for applications making frequent calls.
3. **Limited Flexibility** : The class-based approach made it difficult to implement dynamic configurations and integrate seamlessly with other Python libraries.
4. **Verbose Code** : Users had to write more boilerplate code to set up and execute LLM calls.
5. **Integration Challenges** : Integrating with other Python libraries, especially those using decorators, was not as smooth as we wanted.

## Community Feedback: Shaping Mirascope

Our community has been incredible, providing consistent feedback that has influenced our design and ultimately helped shape V1. For example:

- **Separation of State and Arguments** : Many users wanted to be able to more clearly distinguish between the state managed across multiple calls and the arguments passed in for each individual call. For example, chat history vs. the user's current query.
- **Dynamic Configuration** : We received multiple requests for dynamically configuring calls at runtime based on arguments of the call. One user in particular suggested we use the original decorated function's return for configuration, which was pivotal in how we designed and implemented dynamic configuration.
- **Provider Flexibility** : Consistent requests for easier switching between LLM providers reinforced our commitment to provider-agnostic design. This in no way means not to engineer prompts for a specific provider, but the ability to switch should be present and easy.

It's worth going through our solutions to each of these problems to properly highlight why we made the changes we did in our v1 release. Of course, there were many other points of feedback we addressed as well as additional features we've included in the release.

Take a look at our [migration guide](https://mirascope.com/MIGRATE/) and [learn documentation](https://mirascope.com/learn) for a deeper dive that covers everything in detail.

### Separation of State and Arguments

In V0, state and arguments were mixed as fields of the class, making it difficult and unclear what should persist across calls and what should be specific to each individual call.
‍

```python
from mirascope.openai import OpenAICall


class Librarian(OpenAICall):
    prompt_template = """
    SYSTEM: You are a librarian. You specialize in the {genre} genre
    USER: {query}
    """

    genre: str
    query: str


librarian = Librarian(
    genre="fantasy",
    query="Recommend a book",
)
response = librarian.call()
print(response.content)

librarian.query = "Recommend a book for beginners"
response = librarian.call()
print(response.content)
```

It's not clear to the end user of the `Librarian` class that the `query` field is actually an argument of the call that should be updated across each call. The solution would be to create an entirely new instance of `Librarian` for every call, but this would make both `genre` and `query` feel like arguments.

There was no clear way to separate between `genre` being state and `query` being an argument.

We tried our best to include arguments as part of the `call` and other such methods as an additional keyword argument, but this was unfortunately not possible without losing proper type hints due to limitations with the class-based approach in Python.

With V1, the separation of state and arguments was not only easy to implement but also felt extremely natural to write as an end-user of the interface:

```python
from mirascope.core import openai, prompt_template
from pydantic import BaseModel


class Librarian(BaseModel):
    genre: str

    @openai.call("gpt-4o-mini")
    @prompt_template(
        """
        SYSTEM: You are a librarian. You specialize in the {self.genre} genre
        USER: {query}
        """
    )
    def call(self, query: str): ...


fantasy_librarian = Librarian(genre="fantasy")
response = fantasy_librarian.call("Recommend a book")
print(response.content)

response = fantasy_librarian.call("Recommend a book for beginners")
print(response.content)
```

It's now evident that `genre` is state of the `Librarian` class, and the call method uses this state for every call. However, `query` is now clearly an argument of the call that should be provided for every call that's made.

### Dynamic Configuration

Now that we had separation of state and arguments, we could fully enable dynamic configuration using these call parameters. The biggest change here is the ability to now dynamically generate tools, which was not previously feasible (even after a long back-and-forth with a talented Python engineer extremely experienced with Python typing, who has now joined the team!).

```python
from mirascope.core import BaseToolKit, openai, prompt_template, toolkit_tool


class BookToolkit(BaseToolKit):
    genre: str

    @toolkit_tool
    def format_book(self, title: str, author: str) -> str:
        """Format a {self.genre} book recommendation."""
        return f"{title} by {author} ({self.genre})"


@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
    toolkit = BookToolkit(genre=genre)
    return {"tools": toolkit.create_tools()}


response = recommend_book("mystery")
if response.tool:
    print(response.tool.call())
```

### Provider Flexibility

V0 made it challenging to switch between different LLM providers without significant code changes.

```python
from mirascope.openai import OpenAICall


class BookRecommender(OpenAICall):
    prompt_template = "Recommend a {genre} book."

    genre: str


recommender = BookRecommender(genre="fantasy")
response = recommender.call()
print(response.content)
```

In this example, switching providers would require rewriting the entire class (e.g. switching `OpenAICall` to `AnthropicCall`) with no alternate solution available.

The decorator approach in V1's design makes switching between providers simple. In fact, it's possible to easily run multiple providers on the same prompt with the same configuration:

```python
from mirascope.core import anthropic, openai, prompt_template


@prompt_template()
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


openai_recommend_book = openai.call("gpt-4o-mini")(recommend_book)
openai_response = openai_recommend_book("fantasy")
print(openai_response.content)

anthropic_recommend_book = anthropic.call("claude-3-5-sonnet-20240620")(recommend_book)
anthropic_response = anthropic_recommend_book("fantasy")
print(anthropic_response.content)
```

You can also use the `BasePrompt` class for a more similar interface to v0 and run it against any supported provider's decorator:

```python
from mirascope.core import BasePrompt, anthropic, openai


class BookRecommendationPrompt(BasePrompt):
    prompt_template = "Recommend a {genre} book"

    genre: str


prompt = BookRecommendationPrompt(genre="fantasy")

openai_response = prompt.run(openai.call("gpt-4o-mini"))
print(openai_response.content)

anthropic_response = prompt.run(anthropic.call("claude-3-5-sonnet-20240620"))
print(anthropic_response.content)
```

## Key Learnings

Throughout this process, we've gained valuable insights:

1. **Embrace Statelessness** : LLM API calls are inherently stateless. Designing our package to reflect this leads to cleaner, more efficient code. When we do want to include state (such as for agents), the how and why are extremely clear.
2. **Prioritize Developer Experience** : Simplifying the API and reducing boilerplate significantly improves the developer experience. It makes building with Mirascope the most fun I've had building anything in a long time.
3. **Performance Matters** : Even small overheads can add up in large-scale applications. Optimizing for performance from the ground up is crucial. This is something that we will strive to continuously optimize.
4. **Flexibility is Key** : The AI landscape is rapidly evolving. Building flexibility into the core design allows for easier adaptation to new developments. What happens when a provider releases a new feature? There's no reason for users to wait on us to gain access to these features or otherwise be forced to rip everything out and return to the base SDK.
5. **Community Feedback is Invaluable** : Many of our improvements came from user feedback. Actively engaging with the community leads to a better product.

## Looking Forward

Mirascope V1 is a significant step forward, but our journey doesn't end here. We're committed to continuous improvement and innovation. Some areas we're particularly excited about exploring in future releases include:

- **More Programming Languages** : I started with Python because that's what felt most natural as an MLE / AI research engineer. But I think developers that program with other languages deserve tooling that follows the same principles with which we've built Mirascope. I expect the next language we support will be JavaScript/TypeScript.
- **Provider Support** : New providers (and new features) are popping up all of the time. For example, OpenAI just recently released structured output support natively, and Anthropic just released prompt caching. We want to push ourselves to support such releases as soon as they are released.
- **Version Control** : Versioning a text prompt may be easy, but the reality is that prompts are often far more than just a single text snippet – they involve code. We love git, but it falls short in this instance. We're excited about discovering new ways to support versioning on the fly for better hot-swapping of entire flows to enable easier evaluation and comparison of various implementation versions. We're currently working a new library, [`Lilypad`](https://lilypad.so/docs), which automatically versions and traces LLM functions on every call.
- **Postgres and pgvec** : Similar to improving the ergonomics of LLM APIs, we think there is a single layer abstraction on top of Postgres and pgvec that's waiting to be built. We envision something like a CRUD interface for RAG apps where the underlying data can live where all of your data already lives.

Let us know if there's anything specific you'd like to see included in future releases!

Building Mirascope has been an incredible learning experience. We're incredibly grateful to our community for their support, feedback, and patience throughout this process. Mirascope V1 is as much your achievement as it is ours.

We invite you to try out Mirascope V1, share your experiences, and join us in shaping the future of LLM development in Python. Together, we can continue to push the boundaries of what's possible with AI.

Ready to get started? Here's how:

1. Check out our [Quick Start Guide](https://mirascope.com/tutorials/getting_started/quickstart) to set up Mirascope in minutes.
2. Explore our [Usage Documentation](https://mirascope.com/learn) for in-depth guides and examples.
3. Join our [Slack Community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA) to discuss questions, stay up to date on announcements, or even show off what you've built.

Let's build the future of AI together!
