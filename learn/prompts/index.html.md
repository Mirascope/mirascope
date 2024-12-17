---
search:
  boost: 3
---

# Prompts

When working with Large Language Model (LLM) APIs, the "prompt" is generally a list of messages where each message has a particular role. These prompts are the foundation of effectively working with LLMs, so Mirascope provides powerful tools to help you create, manage, and optimize your prompts for various LLM interactions.

Let's look at how we can write prompts using Mirascope in a reusable, modular, and provider-agnostic way.

!!! info "Calls will come later"

    For the following explanations we will be talking *only* about the messages aspect of prompt engineering and will discuss calling the API later in the [Calls](./calls.md) documentation.
    
    In that section we will show how to use these provider-agnostic prompts to actually call a provider's API as well as how to engineer and tie a prompt to a specific call.

## Prompt Templates (Messages)

??? api "API Documentation"

    [`mirascope.core.base.message_param`](../api/core/base/message_param.md)

    [`mirascope.core.base.prompt.prompt_template`](../api/core/base/prompt.md#mirascope.core.base.prompt.prompt_template)

First, let's look at a basic example:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="4-6 10"
            from mirascope.core import prompt_template


            @prompt_template()
            def recommend_book_prompt(genre: str) -> str:
                return f"Recommend a {genre} book"


            print(recommend_book_prompt("fantasy"))
            # Output: [BaseMessageParam(role='user', content='Recommend a fantasy book')]
        ```
    === "Messages"

        ```python hl_lines="4-6 10"
            from mirascope.core import Messages, prompt_template


            @prompt_template()
            def recommend_book_prompt(genre: str) -> Messages.Type:
                return Messages.User(f"Recommend a {genre} book")


            print(recommend_book_prompt("fantasy"))
            # Output: [BaseMessageParam(role='user', content='Recommend a fantasy book')]
        ```
    === "String Template"

        ```python hl_lines="4-5 9"
            from mirascope.core import prompt_template


            @prompt_template("Recommend a {genre} book")
            def recommend_book_prompt(genre: str): ...


            print(recommend_book_prompt("fantasy"))
            # Output: [BaseMessageParam(role='user', content='Recommend a fantasy book')]
        ```
    === "BaseMessageParam"

        ```python hl_lines="4-6 10"
            from mirascope.core import BaseMessageParam, prompt_template


            @prompt_template()
            def recommend_book_prompt(genre: str) -> list[BaseMessageParam]:
                return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


            print(recommend_book_prompt("fantasy"))
            # Output: [BaseMessageParam(role='user', content='Recommend a fantasy book')]
        ```

In this example:

1. The `recommend_book_prompt` method's signature defines the prompt's template variables.
2. Calling the method with `genre="fantasy"` returns a list with the corresponding `BaseMessageParam` instance with role `user` and content "Recommend a fantasy book".

The core concept to understand here is [`BaseMessageParam`](../api/core/base/message_param.md#basemessageparam). This class operates as the base class for message parameters that Mirascope can handle and use across all supported providers.

In Mirascope, we use the `@prompt_template` decorator to write prompt templates as reusable methods that return the corresponding list of `BaseMessageParam` instances.

There are four methods of writing prompts:

1. _(Shorthand)_ Returning the `str` or `list` content for a single user message.
2. _(Messages)_ Using `Messages.{Role}` methods, which accept the full or shorthand content and output a `BaseMessageParam` instance.
3. _(String Template)_ Passing a string template to `@prompt_template` that gets parsed and then formatted like a normal Python formatted string.
4. _(BaseMessageParam)_ Directly writing `BaseMessageParam` instances.

Which method you use is mostly up to your preference, so feel free to select which one you prefer in the following sections.

## Message Roles

We can also define additional messages with different roles, such as a system message:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="7-8 14-15"
            from mirascope.core import Messages, prompt_template


            @prompt_template()
            def recommend_book_prompt(genre: str) -> Messages.Type:
                return [
                    Messages.System("You are a librarian"),
                    Messages.User(f"Recommend a {genre} book"),
                ]


            print(recommend_book_prompt("fantasy"))
            # Output: [
            #   BaseMessageParam(role='system', content='You are a librarian'),
            #   BaseMessageParam(role='user', content='Recommend a fantasy book'),
            # ]
        ```
    === "Messages"

        ```python hl_lines="7-8 14-15"
            from mirascope.core import Messages, prompt_template


            @prompt_template()
            def recommend_book_prompt(genre: str) -> Messages.Type:
                return [
                    Messages.System("You are a librarian"),
                    Messages.User(f"Recommend a {genre} book"),
                ]


            print(recommend_book_prompt("fantasy"))
            # Output: [
            #   BaseMessageParam(role='system', content='You are a librarian'),
            #   BaseMessageParam(role='user', content='Recommend a fantasy book'),
            # ]
        ```
    === "String Template"

        ```python hl_lines="6-7 15-16"
            from mirascope.core import prompt_template


            @prompt_template(
                """
                SYSTEM: You are a librarian
                USER: Recommend a {genre} book
                """
            )
            def recommend_book_prompt(genre: str): ...


            print(recommend_book_prompt("fantasy"))
            # Output: [
            #   BaseMessageParam(role='system', content='You are a librarian'),
            #   BaseMessageParam(role='user', content='Recommend a fantasy book'),
            # ]
        ```
    === "BaseMessageParam"

        ```python hl_lines="7-8 14-15"
            from mirascope.core import BaseMessageParam, prompt_template


            @prompt_template()
            def recommend_book_prompt(genre: str) -> list[BaseMessageParam]:
                return [
                    BaseMessageParam(role="system", content="You are a librarian"),
                    BaseMessageParam(role="user", content=f"Recommend a {genre} book"),
                ]


            print(recommend_book_prompt("fantasy"))
            # Output: [
            #   BaseMessageParam(role='system', content='You are a librarian'),
            #   BaseMessageParam(role='user', content='Recommend a fantasy book'),
            # ]
        ```

!!! note "`Messages.Type`"

    The return type `Messages.Type` accepts all shorthand methods as well as `BaseMessageParam` types. Since the message methods (e.g. `Messages.User`) return `BaseMessageParam` instances, we generally recommend always typing your prompt templates with the `Messages.Type` return type since it covers all prompt template writing methods.

!!! info "Supported Roles"

    Mirascope prompt templates currently support the `system`, `user`, and `assistant` roles. When using string templates, the roles are parsed by their corresponding all caps keyword (e.g. SYSTEM).

    For messages with the `tool` role, see how Mirascope automatically generates these messages for you in the [Tools](./tools.md) and [Agents](./agents.md) sections.

## Multi-Line Prompts

When writing prompts that span multiple lines, it's important to ensure you don't accidentally include additional, unnecessary tokens (namely `\t` tokens):

!!! mira ""

    === "Shorthand"

        ```python hl_lines="8-13 17"
            import inspect

            from mirascope.core import Messages, prompt_template


            @prompt_template()
            def recommend_book_prompt(genre: str) -> Messages.Type:
                return inspect.cleandoc(
                    f"""
                    Recommend a {genre} book.
                    Output in the format Title by Author.
                    """
                )


            print(recommend_book_prompt("fantasy"))
            # Output: [BaseMessageParam(role='system', content='Recommend a fantasy book.\nOutput in the format Title by Author.')]
        ```
    === "Messages"

        ```python hl_lines="9-14 19"
            import inspect

            from mirascope.core import Messages, prompt_template


            @prompt_template()
            def recommend_book_prompt(genre: str) -> Messages.Type:
                return Messages.User(
                    inspect.cleandoc(
                        f"""
                        Recommend a {genre} book.
                        Output in the format Title by Author.
                        """
                    )
                )


            print(recommend_book_prompt("fantasy"))
            # Output: [BaseMessageParam(role='system', content='Recommend a fantasy book.\nOutput in the format Title by Author.')]
        ```
    === "String Template"

        ```python hl_lines="6-7 14"
            from mirascope.core import prompt_template


            @prompt_template(
                """
                Recommend a {genre} book.
                Output in the format Title by Author.
                """
            )
            def recommend_book_prompt(genre: str): ...


            print(recommend_book_prompt("fantasy"))
            # Output: [BaseMessageParam(role='system', content='Recommend a fantasy book.\nOutput in the format Title by Author.')]
        ```
    === "BaseMessageParam"

        ```python hl_lines="11-16 22"
            import inspect

            from mirascope.core import BaseMessageParam, prompt_template


            @prompt_template()
            def recommend_book_prompt(genre: str) -> list[BaseMessageParam]:
                return [
                    BaseMessageParam(
                        role="user",
                        content=inspect.cleandoc(
                            f"""
                            Recommend a {genre} book.
                            Output in the format Title by Author.
                            """
                        ),
                    ),
                ]


            print(recommend_book_prompt("fantasy"))
            # Output: [BaseMessageParam(role='system', content='Recommend a fantasy book.\nOutput in the format Title by Author.')]
        ```

In this example, we use `inspect.cleandoc` to remove unnecessary tokens while maintaining proper formatting in our codebase.

??? warning "Multi-Line String Templates"

    When using string templates, the template is automatically cleaned for you, so there is no need to use `inspect.cleandoc` in that case. However, it's extremely important to note that you must start messages with the same indentation in order to properly remove the unnecessary tokens. For example:

    ```python
    # BAD
    @prompt_template(
        """
        USER: First line
        Second line
        """
    )

    # GOOD
    @prompt_template(
        """
        USER:
        First line
        Second line
        """
    )
    ```

## Multi-Modal Inputs

Recent advancements in Large Language Model architecture has enabled many model providers to support multi-modal inputs (text, images, audio, etc.) for a single endpoint. Mirascope treats these input types as first-class and supports them natively.

While Mirascope provides a consistent interface, support varies among providers:

| Type          | Anthropic | Cohere | Gemini | Groq | Mistral | OpenAI |
|---------------|-----------|--------|--------|------|---------|--------|
| text          | ✓         | ✓      | ✓      | ✓    | ✓       | ✓      |
| image         | ✓         | -      | ✓      | ✓    | ✓       | ✓      |
| audio         | -         | -      | ✓      | -    | -       | ✓      |
| video         | -         | -      | ✓      | -    | -       | -      |
| document      | ✓         | -      | -      | -    | -       | -      |

Legend: ✓ (Supported), - (Not Supported)

### Image Inputs

!!! mira ""

    === "Shorthand"

        ```python hl_lines="7 16-18"
            from mirascope.core import Messages, prompt_template
            from PIL import Image


            @prompt_template()
            def recommend_book_prompt(previous_book: Image.Image) -> Messages.Type:
                return ["I just read this book:", previous_book, "What should I read next?"]


            with Image.open("...") as image:
                print(recommend_book_prompt(image))
            # Output: [
            #     BaseMessageParam(
            #         role="user",
            #         content=[
            #             TextPart(type="text", text="I just read this book:"),
            #             ImagePart(type="image", media_type="image/jpeg", image=b"...", detail=None),
            #             TextPart(type="text", text="What should I read next?"),
            #         ],
            #     )
            # ]
        ```
    === "Messages"

        ```python hl_lines="8 18-20"
            from mirascope.core import Messages, prompt_template
            from PIL import Image


            @prompt_template()
            def recommend_book_prompt(previous_book: Image.Image) -> Messages.Type:
                return Messages.User(
                    ["I just read this book:", previous_book, "What should I read next?"]
                )


            with Image.open("...") as image:
                print(recommend_book_prompt(image))
            # Output: [
            #     BaseMessageParam(
            #         role="user",
            #         content=[
            #             TextPart(type="text", text="I just read this book:"),
            #             ImagePart(type="image", media_type="image/jpeg", image=b"...", detail=None),
            #             TextPart(type="text", text="What should I read next?"),
            #         ],
            #     )
            # ]
        ```
    === "String Template"

        ```python hl_lines="5 15-17"
            from mirascope.core import prompt_template


            @prompt_template(
                "I just read this book: {previous_book:image} What should I read next?"
            )
            def recommend_book_prompt(previous_book: bytes): ...


            print(recommend_book_prompt(b"..."))
            # Output: [
            #     BaseMessageParam(
            #         role="user",
            #         content=[
            #             TextPart(type="text", text="I just read this book:"),
            #             ImagePart(type="image", media_type="image/jpeg", image=b"...", detail=None),
            #             TextPart(type="text", text="What should I read next?"),
            #         ],
            #     )
            # ]
        ```
    === "BaseMessageParam"

        ```python hl_lines="10-17 28-30"
            from mirascope.core import BaseMessageParam
            from mirascope.core.base import ImagePart, TextPart


            def recommend_book_prompt(previous_book_jpeg: bytes) -> list[BaseMessageParam]:
                return [
                    BaseMessageParam(
                        role="user",
                        content=[
                            TextPart(type="text", text="I just read this book:"),
                            ImagePart(
                                type="image",
                                media_type="image/jpeg",
                                image=previous_book_jpeg,
                                detail=None,
                            ),
                            TextPart(type="text", text="What should I read next?"),
                        ],
                    )
                ]


            print(recommend_book_prompt(b"..."))
            # Output: [
            #     BaseMessageParam(
            #         role="user",
            #         content=[
            #             TextPart(type="text", text="I just read this book:"),
            #             ImagePart(type="image", media_type="image/jpeg", image=b"...", detail=None),
            #             TextPart(type="text", text="What should I read next?"),
            #         ],
            #     )
            # ]
        ```

??? info "Additional String Template Image Functionality"

    When using string templates, you can also specify `:images` to inject multiple image inputs through a single template variable.

    The `:image` and `:images` tags support the `bytes | str` and `list[bytes] | list[str]` types, respectively. When passing in a `str`, the string template assumes it indicates a url or local filepath and will attempt to load the bytes from the source.

    You can also specify additional options as arguments of the tags, e.g. `{url:image(detail=low)}`

### Audio Inputs

!!! mira ""

    === "pydub"
        === "Shorthand"
            ```python hl_lines="8 17-19"
                from pydub import AudioSegment

                from mirascope.core import prompt_template, Messages


                @prompt_template()
                def identify_book_prompt(audio_wave: AudioSegment) -> Messages.Type:
                    return ["Here's an audio book snippet:", audio_wave, "What book is this?"]


                with open("....", "rb") as audio:
                    print(identify_book_prompt(AudioSegment.from_mp3(audio)))
                # Output: [
                #     BaseMessageParam(
                #         role="user",
                #         content=[
                #             TextPart(type="text", text="Here's an audio book snippet:"),
                #             AudioPart(type='audio', media_type='audio/wav', audio=b'...'),
                #             TextPart(type="text", text="What book is this?"),
                #         ],
                #     )
                # ]
            ```
        === "Messages"
            ```python hl_lines="9 19-21"
                from pydub import AudioSegment

                from mirascope.core import prompt_template, Messages


                @prompt_template()
                def identify_book_prompt(audio_wave: AudioSegment) -> Messages.Type:
                    return Messages.User(
                        ["Here's an audio book snippet:", audio_wave, "What book is this?"]
                    )


                with open("....", "rb") as audio:
                    print(identify_book_prompt(AudioSegment.from_mp3(audio)))
                # Output: [
                #     BaseMessageParam(
                #         role="user",
                #         content=[
                #             TextPart(type="text", text="Here's an audio book snippet:"),
                #             AudioPart(type='audio', media_type='audio/wav', audio=b'...'),
                #             TextPart(type="text", text="What book is this?"),
                #         ],
                #     )
                # ]
            ```
        === "String Template"
            ```python hl_lines="4 13-15"
                from mirascope.core import prompt_template


                @prompt_template("Here's an audio book snippet: {audio_wave:audio} What book is this?")
                def identify_book_prompt(audio_wave: bytes): ...


                print(identify_book_prompt(b"..."))
                # Output: [
                #     BaseMessageParam(
                #         role="user",
                #         content=[
                #             TextPart(type="text", text="Here's an audio book snippet:"),
                #             AudioPart(type='audio', media_type='audio/wav', audio=b'...'),
                #             TextPart(type="text", text="What book is this?"),
                #         ],
                #     )
                # ]
            ```
        === "BaseMessageParam"
            ```python hl_lines="10-16 27-29"
                from mirascope.core import BaseMessageParam
                from mirascope.core.base import AudioPart, TextPart


                def identify_book_prompt(audio_wave: bytes) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=[
                                TextPart(type="text", text="Here's an audio book snippet:"),
                                AudioPart(
                                    type="audio",
                                    media_type="audio/wav",
                                    audio=audio_wave,
                                ),
                                TextPart(type="text", text="What book is this?"),
                            ],
                        )
                    ]


                print(identify_book_prompt(b"..."))
                # Output: [
                #     BaseMessageParam(
                #         role="user",
                #         content=[
                #             TextPart(type="text", text="Here's an audio book snippet:"),
                #             AudioPart(type='audio', media_type='audio/mp3', audio=b'...'),
                #             TextPart(type="text", text="What book is this?"),
                #         ],
                #     )
                # ]
            ```
    === "wave"
        === "Shorthand"
            ```python hl_lines="8 17-19"
                import wave

                from mirascope.core import Messages, prompt_template


                @prompt_template()
                def identify_book_prompt(audio_wave: wave.Wave_read) -> Messages.Type:
                    return ["Here's an audio book snippet:", audio_wave, "What book is this?"]


                with open("....", "rb") as f, wave.open(f, "rb") as audio:
                    print(identify_book_prompt(audio))
                # Output: [
                #     BaseMessageParam(
                #         role="user",
                #         content=[
                #             TextPart(type="text", text="Here's an audio book snippet:"),
                #             AudioPart(type='audio', media_type='audio/wav', audio=b'...'),
                #             TextPart(type="text", text="What book is this?"),
                #         ],
                #     )
                # ]
            ```
        === "Messages"
            ```python hl_lines="9 19-21"
                import wave

                from mirascope.core import Messages, prompt_template


                @prompt_template()
                def identify_book_prompt(audio_wave: wave.Wave_read) -> Messages.Type:
                    return Messages.User(
                        ["Here's an audio book snippet:", audio_wave, "What book is this?"]
                    )


                with open("....", "rb") as f, wave.open(f, "rb") as audio:
                    print(identify_book_prompt(audio))
                # Output: [
                #     BaseMessageParam(
                #         role="user",
                #         content=[
                #             TextPart(type="text", text="Here's an audio book snippet:"),
                #             AudioPart(type='audio', media_type='audio/wav', audio=b'...'),
                #             TextPart(type="text", text="What book is this?"),
                #         ],
                #     )
                # ]
            ```
        === "String Template"
            ```python hl_lines="4 13-15"
                from mirascope.core import prompt_template


                @prompt_template("Here's an audio book snippet: {audio_wave:audio} What book is this?")
                def identify_book_prompt(audio_wave: bytes): ...


                print(identify_book_prompt(b"..."))
                # Output: [
                #     BaseMessageParam(
                #         role="user",
                #         content=[
                #             TextPart(type="text", text="Here's an audio book snippet:"),
                #             AudioPart(type='audio', media_type='audio/wav', audio=b'...'),
                #             TextPart(type="text", text="What book is this?"),
                #         ],
                #     )
                # ]
            ```
        === "BaseMessageParam"
            ```python hl_lines="10-16 27-29"
                from mirascope.core import BaseMessageParam
                from mirascope.core.base import AudioPart, TextPart


                def identify_book_prompt(audio_wave: bytes) -> list[BaseMessageParam]:
                    return [
                        BaseMessageParam(
                            role="user",
                            content=[
                                TextPart(type="text", text="Here's an audio book snippet:"),
                                AudioPart(
                                    type="audio",
                                    media_type="audio/wav",
                                    audio=audio_wave,
                                ),
                                TextPart(type="text", text="What book is this?"),
                            ],
                        )
                    ]


                print(identify_book_prompt(b"..."))
                # Output: [
                #     BaseMessageParam(
                #         role="user",
                #         content=[
                #             TextPart(type="text", text="Here's an audio book snippet:"),
                #             AudioPart(type='audio', media_type='audio/mp3', audio=b'...'),
                #             TextPart(type="text", text="What book is this?"),
                #         ],
                #     )
                # ]
            ```

??? info "Additional String Template Audio Functionality"

    When using string templates, you can also specify `:audios` to inject multiple audio inputs through a single template variable.

    The `:audio` and `:audios` tags support the `bytes | str` and `list[bytes] | list[str]` types, respectively. When passing in a `str`, the string template assumes it indicates a url or local filepath and will attempt to load the bytes from the source.

### Document Inputs

!!! mira ""

    === "Shorthand"

        ```python hl_lines="10-16 27-29"
            # Not supported
        ```
    === "Messages"

        ```python hl_lines="10-16 27-29"
            # Not supported
        ```
    === "String Template"

        ```python hl_lines="5 15-17"
            from mirascope.core import prompt_template


            @prompt_template(
                "I just read this book: {previous_book:document} What should I read next?"
            )
            def recommend_book_prompt(previous_book: bytes): ...


            print(recommend_book_prompt(b"..."))
            # Output: [
            #     BaseMessageParam(
            #         role="user",
            #         content=[
            #             TextPart(type="text", text="I just read this book:"),
            #             DocumentPart(type='document', media_type='application/pdf', document=b'...'),
            #             TextPart(type="text", text="What should I read next?"),
            #         ],
            #     )
            # ]
        ```
    === "BaseMessageParam"

        ```python hl_lines="10-16 27-29"
            from mirascope.core import BaseMessageParam
            from mirascope.core.base import DocumentPart, TextPart


            def recommend_book_prompt(previous_book_pdf: bytes) -> list[BaseMessageParam]:
                return [
                    BaseMessageParam(
                        role="user",
                        content=[
                            TextPart(type="text", text="I just read this book:"),
                            DocumentPart(
                                type="document",
                                media_type="application/pdf",
                                document=previous_book_pdf,
                            ),
                            TextPart(type="text", text="What should I read next?"),
                        ],
                    )
                ]


            print(recommend_book_prompt(b"..."))
            # Output: [
            #     BaseMessageParam(
            #         role="user",
            #         content=[
            #             TextPart(type="text", text="I just read this book:"),
            #             DocumentPart(type='document', media_type='application/pdf', document=b'...'),
            #             TextPart(type="text", text="What should I read next?"),
            #         ],
            #     )
            # ]
        ```

!!! warning "Support Document Types"

    Currently, only Anthropic supports the `:document` specifier, and only PDF documents are supported.

??? info "Additional String Template Document Functionality"

    When using string templates, you can also specify `:documents` to inject multiple audio inputs through a single template variable.

    The `:document` and `:documents` tags support the `bytes | str` and `list[bytes] | list[str]` types, respectively. When passing in a `str`, the string template assumes it indicates a url or local filepath and will attempt to load the bytes from the source.

## Chat History

Often you'll want to inject messages (such as previous chat messages) into the prompt. Generally you can just unroll the messages into the return value of your prompt template. When using string templates, we provide a `MESSAGES` keyword for this injection, which you can add in whatever position and as many times as you'd like:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="6 10-11 15-18"
            from mirascope.core import BaseMessageParam, Messages, prompt_template


            @prompt_template()
            def chatbot(query: str, history: list[BaseMessageParam]) -> list[BaseMessageParam]:
                return [Messages.System("You are a librarian"), *history, Messages.User(query)]


            history = [
                Messages.User("Recommend a book"),
                Messages.Assistant("What genre do you like?"),
            ]
            print(chatbot("fantasy", history))
            # Output: [
            #     BaseMessageParam(role="system", content="You are a librarian"),
            #     BaseMessageParam(role="user", content="Recommend a book"),
            #     BaseMessageParam(role="assistant", content="What genre do you like?"),
            #     BaseMessageParam(role="user", content="fantasy"),
            # ]
        ```
    === "Messages"

        ```python hl_lines="6 10-11 15-18"
            from mirascope.core import BaseMessageParam, Messages, prompt_template


            @prompt_template()
            def chatbot(query: str, history: list[BaseMessageParam]) -> list[BaseMessageParam]:
                return [Messages.System("You are a librarian"), *history, Messages.User(query)]


            history = [
                Messages.User("Recommend a book"),
                Messages.Assistant("What genre do you like?"),
            ]
            print(chatbot("fantasy", history))
            # Output: [
            #     BaseMessageParam(role="system", content="You are a librarian"),
            #     BaseMessageParam(role="user", content="Recommend a book"),
            #     BaseMessageParam(role="assistant", content="What genre do you like?"),
            #     BaseMessageParam(role="user", content="fantasy"),
            # ]
        ```
    === "String Template"

        ```python hl_lines="6-8 15-16 20-23"
            from mirascope.core import BaseMessageParam, Messages, prompt_template


            @prompt_template(
                """
                SYSTEM: You are a librarian
                MESSAGES: {history}
                USER: {query}
                """
            )
            def chatbot(query: str, history: list[BaseMessageParam]): ...


            history = [
                Messages.User("Recommend a book"),
                Messages.Assistant("What genre do you like?"),
            ]
            print(chatbot("fantasy", history))
            # Output: [
            #     BaseMessageParam(role="system", content="You are a librarian"),
            #     BaseMessageParam(role="user", content="Recommend a book"),
            #     BaseMessageParam(role="assistant", content="What genre do you like?"),
            #     BaseMessageParam(role="user", content="fantasy"),
            # ]
        ```
    === "BaseMessageParam"

        ```python hl_lines="7-9 14-15 19-22"
            from mirascope.core import BaseMessageParam, prompt_template


            @prompt_template()
            def chatbot(query: str, history: list[BaseMessageParam]) -> list[BaseMessageParam]:
                return [
                    BaseMessageParam(role="system", content="You are a librarian"),
                    *history,
                    BaseMessageParam(role="user", content=query),
                ]


            history = [
                BaseMessageParam(role="user", content="Recommend a book"),
                BaseMessageParam(role="assistant", content="What genre do you like?"),
            ]
            print(chatbot("fantasy", history))
            # Output: [
            #     BaseMessageParam(role="system", content="You are a librarian"),
            #     BaseMessageParam(role="user", content="Recommend a book"),
            #     BaseMessageParam(role="assistant", content="What genre do you like?"),
            #     BaseMessageParam(role="user", content="fantasy"),
            # ]
        ```

## Object Attribute Access

When using template variables that have attributes, you can easily inject these attributes directly even when using string templates:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="12 17"
            from mirascope.core import prompt_template
            from pydantic import BaseModel


            class Book(BaseModel):
                title: str
                author: str


            @prompt_template()
            def recommend_book_prompt(book: Book) -> str:
                return f"I read {book.title} by {book.author}. What should I read next?"


            book = Book(title="The Name of the Wind", author="Patrick Rothfuss")
            print(recommend_book_prompt(book))
            # Output: [BaseMessageParam(role='user', content='I read The Name of the Wind by Patrick Rothfuss. What should I read next?')]
        ```
    === "Messages"

        ```python hl_lines="13 19"
            from mirascope.core import Messages, prompt_template
            from pydantic import BaseModel


            class Book(BaseModel):
                title: str
                author: str


            @prompt_template()
            def recommend_book_prompt(book: Book) -> Messages.Type:
                return Messages.User(
                    f"I read {book.title} by {book.author}. What should I read next?"
                )


            book = Book(title="The Name of the Wind", author="Patrick Rothfuss")
            print(recommend_book_prompt(book))
            # Output: [BaseMessageParam(role='user', content='I read The Name of the Wind by Patrick Rothfuss. What should I read next?')]
        ```
    === "String Template"

        ```python hl_lines="10 16"
            from mirascope.core import prompt_template
            from pydantic import BaseModel


            class Book(BaseModel):
                title: str
                author: str


            @prompt_template("I read {book.title} by {book.author}. What should I read next?")
            def recommend_book_prompt(book: Book): ...


            book = Book(title="The Name of the Wind", author="Patrick Rothfuss")
            print(recommend_book_prompt(book))
            # Output: [BaseMessageParam(role='user', content='I read The Name of the Wind by Patrick Rothfuss. What should I read next?')]
        ```
    === "BaseMessageParam"

        ```python hl_lines="15 22"
            from mirascope.core import BaseMessageParam, prompt_template
            from pydantic import BaseModel


            class Book(BaseModel):
                title: str
                author: str


            @prompt_template()
            def recommend_book_prompt(book: Book) -> list[BaseMessageParam]:
                return [
                    BaseMessageParam(
                        role="user",
                        content=f"I read {book.title} by {book.author}. What should I read next?",
                    )
                ]


            book = Book(title="The Name of the Wind", author="Patrick Rothfuss")
            print(recommend_book_prompt(book))
            # Output: [BaseMessageParam(role='user', content='I read The Name of the Wind by Patrick Rothfuss. What should I read next?')]
        ```

It's worth noting that this also works with `self` when using prompt templates inside of a class, which is particularly important when building [Agents](./agents.md).

## Format Specifiers

Since Mirascope prompt templates are just formatted strings, standard Python format specifiers work as expected:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="6 10"
            from mirascope.core import prompt_template


            @prompt_template()
            def recommend_book(genre: str, price: float) -> str:
                return f"Recommend a {genre} book under ${price:.2f}"


            print(recommend_book("fantasy", 12.3456))
            # Output: [BaseMessageParam(role='user', content='Recommend a fantasy book under $12.35')]
        ```
    === "Messages"

        ```python hl_lines="6 10"
            from mirascope.core import Messages, prompt_template


            @prompt_template()
            def recommend_book(genre: str, price: float) -> Messages.Type:
                return Messages.User(f"Recommend a {genre} book under ${price:.2f}")


            print(recommend_book("fantasy", 12.3456))
            # Output: [BaseMessageParam(role='user', content='Recommend a fantasy book under $12.35')]
        ```
    === "String Template"

        ```python hl_lines="4 9"
            from mirascope.core import prompt_template


            @prompt_template("Recommend a {genre} book under ${price:.2f}")
            def recommend_book(genre: str, price: float): ...


            print(recommend_book("fantasy", 12.3456))
            # Output: [BaseMessageParam(role='user', content='Recommend a fantasy book under $12.35')]
        ```
    === "BaseMessageParam"

        ```python hl_lines="8 14"
            from mirascope.core import BaseMessageParam, prompt_template


            @prompt_template()
            def recommend_book(genre: str, price: float) -> list[BaseMessageParam]:
                return [
                    BaseMessageParam(
                        role="user", content=f"Recommend a {genre} book under ${price:.2f}"
                    )
                ]


            print(recommend_book("fantasy", 12.3456))
            # Output: [BaseMessageParam(role='user', content='Recommend a fantasy book under $12.35')]
        ```

When writing string templates, we also offer additional `list` and `lists` format specifiers for convenience around formatting lists:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="8-9 13 16 32 38-48"
            import inspect

            from mirascope.core import prompt_template


            @prompt_template()
            def recommend_book_prompt(genres: list[str], examples: list[list[str]]) -> str:
                formatted_genres = "\n".join(genres)
                formatted_examples = "\n\n".join(["\n".join(e) for e in examples])
                return inspect.cleandoc(
                    """
                    Recommend a book from one of the following genres:
                    {genres}

                    Examples:
                    {examples}
                    """
                ).format(genres=formatted_genres, examples=formatted_examples)


            prompt = recommend_book_prompt(
                genres=["fantasy", "scifi", "mystery"],
                examples=[
                    ["Title: The Name of the Wind", "Author: Patrick Rothfuss"],
                    ["Title: Mistborn: The Final Empire", "Author: Brandon Sanderson"],
                ],
            )
            print(prompt)
            # Output: [
            #     BaseMessageParam(
            #         role="user",
            #         content="Recommend a book from one of the following genres:\nfantasy\nscifi\nmystery\n\nExamples:\nTitle: The Name of the Wind\nAuthor: Patrick Rothfuss\n\nTitle: Mistborn: The Final Empire\nAuthor: Brandon Sanderson",
            #     )
            # ]

            print(prompt[0].content)
            # Output:
            # Recommend a book from one of the following genres:
            # fantasy
            # scifi
            # mystery

            # Examples:
            # Title: The Name of the Wind
            # Author: Patrick Rothfuss

            # Title: Mistborn: The Final Empire
            # Author: Brandon Sanderson
        ```
    === "Messages"

        ```python hl_lines="10-11 16 19 36 42-52"
            import inspect

            from mirascope.core import Messages, prompt_template


            @prompt_template()
            def recommend_book_prompt(
                genres: list[str], examples: list[list[str]]
            ) -> Messages.Type:
                formatted_genres = "\n".join(genres)
                formatted_examples = "\n\n".join(["\n".join(e) for e in examples])
                return Messages.User(
                    inspect.cleandoc(
                        """
                        Recommend a book from one of the following genres:
                        {genres}

                        Examples:
                        {examples}
                        """
                    ).format(genres=formatted_genres, examples=formatted_examples)
                )


            prompt = recommend_book_prompt(
                genres=["fantasy", "scifi", "mystery"],
                examples=[
                    ["Title: The Name of the Wind", "Author: Patrick Rothfuss"],
                    ["Title: Mistborn: The Final Empire", "Author: Brandon Sanderson"],
                ],
            )
            print(prompt)
            # Output: [
            #     BaseMessageParam(
            #         role="user",
            #         content="Recommend a book from one of the following genres:\nfantasy\nscifi\nmystery\n\nExamples:\nTitle: The Name of the Wind\nAuthor: Patrick Rothfuss\n\nTitle: Mistborn: The Final Empire\nAuthor: Brandon Sanderson",
            #     )
            # ]

            print(prompt[0].content)
            # Output:
            # Recommend a book from one of the following genres:
            # fantasy
            # scifi
            # mystery

            # Examples:
            # Title: The Name of the Wind
            # Author: Patrick Rothfuss

            # Title: Mistborn: The Final Empire
            # Author: Brandon Sanderson
        ```
    === "String Template"

        ```python hl_lines="7 10 27 33-43"
            from mirascope.core import prompt_template


            @prompt_template(
                """
                Recommend a book from one of the following genres:
                {genres:list}

                Examples:
                {examples:lists}
                """
            )
            def recommend_book_prompt(genres: list[str], examples: list[list[str]]): ...


            prompt = recommend_book_prompt(
                genres=["fantasy", "scifi", "mystery"],
                examples=[
                    ["Title: The Name of the Wind", "Author: Patrick Rothfuss"],
                    ["Title: Mistborn: The Final Empire", "Author: Brandon Sanderson"],
                ],
            )
            print(prompt)
            # Output: [
            #     BaseMessageParam(
            #         role="user",
            #         content="Recommend a book from one of the following genres:\nfantasy\nscifi\nmystery\n\nExamples:\nTitle: The Name of the Wind\nAuthor: Patrick Rothfuss\n\nTitle: Mistborn: The Final Empire\nAuthor: Brandon Sanderson",
            #     )
            # ]

            print(prompt[0].content)
            # Output:
            # Recommend a book from one of the following genres:
            # fantasy
            # scifi
            # mystery

            # Examples:
            # Title: The Name of the Wind
            # Author: Patrick Rothfuss

            # Title: Mistborn: The Final Empire
            # Author: Brandon Sanderson
        ```
    === "BaseMessageParam"

        ```python hl_lines="10-11 18 21 39 45-55"
            import inspect

            from mirascope.core import BaseMessageParam, prompt_template


            @prompt_template()
            def recommend_book_prompt(
                genres: list[str], examples: list[list[str]]
            ) -> list[BaseMessageParam]:
                formatted_genres = "\n".join(genres)
                formatted_examples = "\n\n".join(["\n".join(e) for e in examples])
                return [
                    BaseMessageParam(
                        role="user",
                        content=inspect.cleandoc(
                            """
                            Recommend a book from one of the following genres:
                            {genres}

                            Examples:
                            {examples}
                            """
                        ).format(genres=formatted_genres, examples=formatted_examples),
                    )
                ]


            prompt = recommend_book_prompt(
                genres=["fantasy", "scifi", "mystery"],
                examples=[
                    ["Title: The Name of the Wind", "Author: Patrick Rothfuss"],
                    ["Title: Mistborn: The Final Empire", "Author: Brandon Sanderson"],
                ],
            )
            print(prompt)
            # Output: [
            #     BaseMessageParam(
            #         role="user",
            #         content="Recommend a book from one of the following genres:\nfantasy\nscifi\nmystery\n\nExamples:\nTitle: The Name of the Wind\nAuthor: Patrick Rothfuss\n\nTitle: Mistborn: The Final Empire\nAuthor: Brandon Sanderson",
            #     )
            # ]

            print(prompt[0].content)
            # Output:
            # Recommend a book from one of the following genres:
            # fantasy
            # scifi
            # mystery

            # Examples:
            # Title: The Name of the Wind
            # Author: Patrick Rothfuss

            # Title: Mistborn: The Final Empire
            # Author: Brandon Sanderson
        ```

## Computed Fields (Dynamic Configuration)

In Mirascope, we write prompt templates as functions, which enables dynamically configuring our prompts at runtime depending on the values of the template variables. We use the term "computed fields" to talk about variables that are computed and formatted at runtime.

In the following examples, we demonstrate using computed fields and dynamic configuration across all prompt templating methods. Of course, this is only actually necessary for string templates. For other methods you can simply format the computed fields directly and return `Messages.Type` as before.

However, there is value in always dynamically configuring computed fields for any and all prompt templating methods. While we cover this in more detail in the [Calls](./calls.md) and [Chaining](./chaining.md) sections, the short of it is that it enables proper tracing even across nested calls and chains.

!!! mira ""

    === "Shorthand"

        ```python hl_lines="6-7 9-10 16-17"
            from mirascope.core import BaseDynamicConfig, Messages, prompt_template


            @prompt_template()
            def recommend_book_prompt(genre: str) -> BaseDynamicConfig:
                uppercase_genre = genre.upper()
                messages = [Messages.User(f"Recommend a {uppercase_genre} book")]
                return {
                    "messages": messages,
                    "computed_fields": {"uppercase_genre": uppercase_genre},
                }


            print(recommend_book_prompt("fantasy"))
            # Output: {
            #     "messages": [BaseMessageParam(role="user", content="Recommend a FANTASY book")],
            #     "computed_fields": {"uppercase_genre": "FANTASY"},
            # }
        ```
    === "Messages"

        ```python hl_lines="6-7 9-10 16-17"
            from mirascope.core import BaseDynamicConfig, Messages, prompt_template


            @prompt_template()
            def recommend_book_prompt(genre: str) -> BaseDynamicConfig:
                uppercase_genre = genre.upper()
                messages = [Messages.User(f"Recommend a {uppercase_genre} book")]
                return {
                    "messages": messages,
                    "computed_fields": {"uppercase_genre": uppercase_genre},
                }


            print(recommend_book_prompt("fantasy"))
            # Output: {
            #     "messages": [BaseMessageParam(role="user", content="Recommend a FANTASY book")],
            #     "computed_fields": {"uppercase_genre": "FANTASY"},
            # }
        ```
    === "String Template"

        ```python hl_lines="4 6 8 13"
            from mirascope.core import BaseDynamicConfig, prompt_template


            @prompt_template("Recommend a {uppercase_genre} book")
            def recommend_book_prompt(genre: str) -> BaseDynamicConfig:
                uppercase_genre = genre.upper()
                return {
                    "computed_fields": {"uppercase_genre": uppercase_genre},
                }


            print(recommend_book_prompt("fantasy"))
            # Output: [BaseMessageParam(role='user', content='Recommend a FANTASY book')]
        ```
    === "BaseMessageParam"

        ```python hl_lines="6 8 11-12 19-20"
            from mirascope.core import BaseDynamicConfig, BaseMessageParam, prompt_template


            @prompt_template()
            def recommend_book_prompt(genre: str) -> BaseDynamicConfig:
                uppercase_genre = genre.upper()
                messages = [
                    BaseMessageParam(role="user", content=f"Recommend a {uppercase_genre} book")
                ]
                return {
                    "messages": messages,
                    "computed_fields": {"uppercase_genre": uppercase_genre},
                }


            print(recommend_book_prompt("fantasy"))
            print(recommend_book_prompt("fantasy"))
            # Output: {
            #     "messages": [BaseMessageParam(role="user", content="Recommend a FANTASY book")],
            #     "computed_fields": {"uppercase_genre": "FANTASY"},
            # }
        ```

There are various other parts of an LLM API call that we may want to configure dynamically as well, such as call parameters, tools, and more. We cover such cases in each of their respective sections.

## Next Steps

By mastering prompts in Mirascope, you'll be well-equipped to build robust, flexible, and reusable LLM applications.

Next, we recommend taking a look at the [Calls](./calls.md) documentation, which shows you how to use your prompt templates to actually call LLM APIs and generate a response.
