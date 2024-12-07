# Anthropic-Specific Features

## Prompt Caching

Anthropic's prompt caching feature can help save a lot of tokens by caching parts of your prompt. For full details, we recommend reading [their documentation](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching).

!!! warning "This Feature Is In Beta"

    While we've added support for prompt caching with Anthropic, this feature is still in beta and requires setting extra headers. You can set this header as an additional call parameter.

    As this feature is in beta, there may be changes made by Anthropic that may result in changes in our own handling of this feature.

### Message Caching

To cache messages, simply add a `:cache_control` tagged breakpoint to your prompt:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="11 24"
            import inspect

            from mirascope.core import Messages, anthropic
            from mirascope.core.base import CacheControlPart


            @anthropic.call(
                "claude-3-5-sonnet-20240620",
                call_params={
                    "max_tokens": 1024,
                    "extra_headers": {"anthropic-beta": "prompt-caching-2024-07-31"},
                },
            )
            def analyze_book(query: str, book: str) -> Messages.Type:
                return [
                    Messages.System(
                        [
                            inspect.cleandoc(f"""
                        You are an AI assistant tasked with analyzing literary works.
                        Your goal is to provide insightful commentary on themes, characters, and writing style.
                            
                        Here is the book in it's entirety: {book}
                        """),
                            CacheControlPart(type="cache_control", cache_type="ephemeral"),
                        ]
                    ),
                    Messages.User(query),
                ]


            print(analyze_book("What are the major themes?", "[FULL BOOK HERE]"))
        ```
    === "Messages"

        ```python hl_lines="11 24"
            import inspect

            from mirascope.core import Messages, anthropic
            from mirascope.core.base import CacheControlPart


            @anthropic.call(
                "claude-3-5-sonnet-20240620",
                call_params={
                    "max_tokens": 1024,
                    "extra_headers": {"anthropic-beta": "prompt-caching-2024-07-31"},
                },
            )
            def analyze_book(query: str, book: str) -> Messages.Type:
                return [
                    Messages.System(
                        [
                            inspect.cleandoc(f"""
                        You are an AI assistant tasked with analyzing literary works.
                        Your goal is to provide insightful commentary on themes, characters, and writing style.
                            
                        Here is the book in it's entirety: {book}
                        """),
                            CacheControlPart(type="cache_control", cache_type="ephemeral"),
                        ]
                    ),
                    Messages.User(query),
                ]


            print(analyze_book("What are the major themes?", "[FULL BOOK HERE]"))
        ```
    === "String Template"

        ```python hl_lines="8 19"
            from mirascope.core import anthropic, prompt_template


            @anthropic.call(
                "claude-3-5-sonnet-20240620",
                call_params={
                    "max_tokens": 1024,
                    "extra_headers": {"anthropic-beta": "prompt-caching-2024-07-31"},
                },
            )
            @prompt_template(
                """
                SYSTEM:
                You are an AI assistant tasked with analyzing literary works.
                Your goal is to provide insightful commentary on themes, characters, and writing style.

                Here is the book in it's entirety: {book}

                {:cache_control}

                USER: {query}
                """
            )
            def analyze_book(query: str, book: str): ...


            print(analyze_book("What are the major themes?", "[FULL BOOK HERE]"))
        ```
    === "BaseMessageParam"

        ```python hl_lines="11 28"
            import inspect

            from mirascope.core import BaseMessageParam, anthropic
            from mirascope.core.base import CacheControlPart, TextPart


            @anthropic.call(
                "claude-3-5-sonnet-20240620",
                call_params={
                    "max_tokens": 1024,
                    "extra_headers": {"anthropic-beta": "prompt-caching-2024-07-31"},
                },
            )
            def analyze_book(query: str, book: str) -> list[BaseMessageParam]:
                return [
                    BaseMessageParam(
                        role="system",
                        content=[
                            TextPart(
                                type="text",
                                text=inspect.cleandoc(f"""
                        You are an AI assistant tasked with analyzing literary works.
                        Your goal is to provide insightful commentary on themes, characters, and writing style.
                            
                        Here is the book in it's entirety: {book}
                        """),
                            ),
                            CacheControlPart(type="cache_control", cache_type="ephemeral"),
                        ],
                    ),
                    BaseMessageParam(role="user", content=query),
                ]


            print(analyze_book("What are the major themes?", "[FULL BOOK HERE]"))
        ```

??? info "Additional options with string templates"

    When using string templates, you can also specify the cache control type the same way we support additional options for multimodal parts (although currently `"ephemeral"` is the only supported type):

    ```python
    @prompt_template("... {:cache_control(type=ephemeral)}")
    ```

### Tool Caching

It is also possible to cache tools by using the `AnthropicToolConfig` and setting the cache control:

!!! mira ""

    ```python hl_lines="8 16 19"
        from mirascope.core import BaseTool, anthropic
        from mirascope.core.anthropic import AnthropicToolConfig


        class CachedTool(BaseTool):
            """This is an example of a cached tool."""

            tool_config = AnthropicToolConfig(cache_control={"type": "ephemeral"})

            def call(self) -> str:
                return "Example tool"


        @anthropic.call(
            "claude-3-5-sonnet-20240620",
            tools=[CachedTool],
            call_params={
                "max_tokens": 1024,
                "extra_headers": {"anthropic-beta": "prompt-caching-2024-07-31"},
            },
        )
        def cached_tool_call() -> str:
            return "An example call with a cached tool"
    ```

Remember only to include the cache control on the last tool in your list of tools that you want to cache (as all tools up to the tool with a cache control breakpoint will be cached).
