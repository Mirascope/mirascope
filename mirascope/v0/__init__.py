import warnings
from contextlib import suppress

from . import base

with suppress(ImportError):
    from . import anthropic

with suppress(ImportError):
    from . import openai


warnings.warn("""MIRASCOPE LOOK-ALIKE V0 INTERFACE USAGE
    You are using the `mirascope.v0` module, which implements look-alike interfaces.
    It is extremely important to note the following about these interfaces:
        - We provide no guarantee that we will support these interfaces. This includes any additional features or bugfixes.
        - We reserve the right to remove these interfaces from the library entirely.
        - These interfaces are an attempt at replicating the v0 interfaces, but they are built using v1 under the hood.
        - This means that you can access certain v1 features through these interfaces (such as multimodal prompt templates).
        - However, this also means that there are inevitable differences (e.g. `OpenAICallResponse` returned from `call` is the `v1` implementation).
    
    The goal of these interfaces is to make it possible to migrate from v0 to v1 without requiring a full migration.
    HOWEVER, there are a few key differences to note:
        - STREAMING:
            - Was annoying to replicate, so we have instead opted to support streaming with the v1 return typing.
            - The return type is a tuple[Chunk, Tool], so if you're not using tools, simply ignore the second item (e.g. `for chunk, _ in stream: ...`)
            - If you're using tools, simply access tools as they are streamed through the second tuple item (i.e. no more `OpenAIToolStream`)
        - BASE CONFIG:
            - Was also annoying to replicate, so we've opted not to replicate this.
            - To provide a custom client (e.g. `AzureOpenAI`), simply pass that client into your function (e.g. `book_recommender.call(client=AzureOpenAI(...))`) and we'll use it.
            - This means there is no longer a `BaseConfig` object on anything.
        - We currently only support the v0 look-alike interfaces for Anthropic and OpenAI.
        - The import structure may differ slightly. In particular, there are no submodules for `anthropic` or `openai`, so you should be importing directly from those modules (e.g. `from mirascope.v0.openai import OpenAICall`)
              
    Next steps:
        - We encourage you to try out the new v1 interface and mirgrate over. We think it's a big improvement, and we hope you will come to feel this way too.
              - We've written a migration guide to help with this process: https://mirascope.com/MIGRATE
        - We greatly appreciate any and all questions/comments/feedback, so if you have anything, send it our way!
        - We understand that some people may prefer the class approach from v0 interface design. You can achieve a very similar interface using v1, see https://mirascope.com/MIGRATE/#baseprompt
        - If there turns out to be sufficient desire for the class-based interfaces to be included in v1 as fully supported interfaces, we will potentially consider this.
""")

__all__ = ["anthropic", "base", "openai"]
