# OpenAI-Specific Features

## Structured Outputs

OpenAI's newest models (starting with `gpt-4o-2024-08-06`) support [strict structured outputs](https://platform.openai.com/docs/guides/structured-outputs) that reliably adhere to developer-supplied JSON Schemas, achieving 100% reliability in their evals, perfectly matching the desired output schemas.

This feature can be extremely useful when extracting structured information or using tools, and you can access this feature when using tools or response models with Mirascope.

### Tools

To use structured outputs with tools, use the `OpenAIToolConfig` and set `strict=True`. You can then use the tool as described in our [Tools documentation](../tools.md):

!!! mira ""

    ```python hl_lines="9"
        from mirascope.core import BaseTool, openai
        from mirascope.core.openai import OpenAIToolConfig


        class FormatBook(BaseTool):
            title: str
            author: str

            tool_config = OpenAIToolConfig(strict=True)

            def call(self) -> str:
                return f"{self.title} by {self.author}"


        @openai.call(
            "gpt-4o-2024-08-06", tools=[FormatBook], call_params={"tool_choice": "required"}
        )
        def recommend_book(genre: str) -> str:
            return f"Recommend a {genre} book"


        response = recommend_book("fantasy")
        if tool := response.tool:
            print(tool.call())
    ```

Under the hood, Mirascope generates a JSON Schema for the `FormatBook` tool based on its attributes and the `OpenAIToolConfig`. This schema is then used by OpenAI's API to ensure the model's output strictly adheres to the defined structure.

### Response Models

Similarly, you can use structured outputs with response models by setting `strict=True` in the response model's `ResponseModelConfigDict`, which is just a subclass of Pydantic's `ConfigDict` with the addition of the `strict` key. You will also need to set `json_mode=True`:

!!! mira ""

    ```python hl_lines="9"
        from mirascope.core import ResponseModelConfigDict, openai
        from pydantic import BaseModel


        class Book(BaseModel):
            title: str
            author: str

            model_config = ResponseModelConfigDict(strict=True)


        @openai.call("gpt-4o-2024-08-06", response_model=Book, json_mode=True)
        def recommend_book(genre: str) -> str:
            return f"Recommend a {genre} book"


        book = recommend_book("fantasy")
        print(book)
    ```

## OpenAI Realtime API (Beta)

Mirascope provides a simple and intuitive way to leverage [OpenAI's cutting-edge Realtime API](https://platform.openai.com/docs/guides/realtime). This integration allows developers to easily create dynamic, interactive applications with real-time audio and text capabilities, all while abstracting away the complexities of WebSocket management and event handling.

With Mirascope, you can quickly set up and use advanced features of OpenAI's Realtime API without dealing with low-level WebSocket operations or complex event structures. This allows you to focus on building your application logic rather than worrying about the intricacies of API communication.

!!! warning "Beta Feature"
    The OpenAI Realtime API integration is currently in beta. As such, the interface is subject to change in future releases. We recommend using this feature with caution in production environments and staying updated with the latest documentation and releases.

### Key Features

Mirascope's OpenAI Realtime API wrapper offers a range of powerful features that make it easy to build sophisticated real-time applications:

- **Audio Input/Output**: Seamlessly handle both audio input from users and audio output from the model, enabling natural voice interactions.
- **Audio Stream Input**: Support for streaming audio input, allowing for real-time processing of continuous audio data.
- **Text Input/Output**: Easily manage text-based interactions alongside audio, providing flexibility in communication modes.
- **Audio Transcript Output**: Automatically receive transcripts of audio outputs, useful for logging, display, or further processing.
- **Multi-modal Interactions**: Combine audio and text modalities in the same session for rich, flexible user experiences.
- **Simplified Session Management**: Abstract away the complexities of WebSocket connections and session handling.
- **Easy-to-use Decorator Pattern**: Utilize intuitive Python decorators to define senders and receivers, streamlining your code structure.
- **Asynchronous Support**: Built-in support for asynchronous operations, allowing for efficient handling of I/O-bound tasks.
- **Tool Integration**: Incorporate custom tools into your Realtime API interactions, enabling more complex and dynamic conversations. Tools can be easily defined as functions and integrated into senders, allowing the AI model to use them during the interaction.
- **Flexible Tool Handling**: Receive and process tool calls from the AI model, enabling your application to perform specific actions or retrieve information as part of the conversation flow.

- These features enable developers to create a wide range of applications, from voice assistants and interactive chatbots to complex multi-modal AI systems, all while leveraging the power of OpenAI's latest models through a clean, Pythonic interface.


### Basic Usage

To use the `Realtime` class, create an instance with the desired model and configure senders and receivers for handling input and output. Mirascope uses Python decorators to simplify the process of defining senders and receivers.

Here's a complete example demonstrating how to set up a streaming audio interaction:

!!! mira ""

    ```python
        import asyncio
        from io import BytesIO

        from typing import AsyncGenerator, Any

        from pydub import AudioSegment
        from pydub.playback import play

        from mirascope.beta.openai import Realtime, record_as_stream

        app = Realtime(
            "gpt-4o-realtime-preview-2024-10-01",
        )


        @app.receiver("audio")
        async def receive_audio(response: AudioSegment, context: dict[str, Any]) -> None:
            play(response)


        @app.receiver("audio_transcript")
        async def receive_audio_transcript(response: str, context: dict[str, Any]) -> None:
            print(f"AI(audio_transcript): {response}")


        @app.sender()
        async def send_audio_as_stream(
            context: dict[str, Any],
        ) -> AsyncGenerator[BytesIO, None]:
            print("Sending audio...")
            async for stream in record_as_stream():
                yield stream


        asyncio.run(app.run())
    ```

Let's break down the key components of this example:

1. First, we create a `Realtime` instance with the specified model:

    !!! mira ""

        ```python

            app = Realtime(
                "gpt-4o-realtime-preview-2024-10-01",
            )
        ```

2. We define two receivers using the `@app.receiver` decorator:

    !!! mira ""

        ```python
            @app.receiver("audio")
            async def receive_audio(response: AudioSegment, context: dict[str, Any]) -> None:
                play(response)


            @app.receiver("audio_transcript")
            async def receive_audio_transcript(response: str, context: dict[str, Any]) -> None:
                print(f"AI(audio_transcript): {response}")
        ```

    The first receiver handles audio responses by playing them, while the second receiver prints the audio transcript.
3. We define a sender using the `@app.sender` decorator:

    !!! mira ""

        ```python
            async def send_audio_as_stream(
                context: dict[str, Any],
            ) -> AsyncGenerator[BytesIO, None]:
                print("Sending audio...")
                async for stream in record_as_stream():
                    yield stream
        ```

   This sender function streams audio data to the model using the `record_as_stream()` function.

4. Finally, we run the application:

    !!! mira ""

        ```python
            asyncio.run(app.run())
        ```

This example demonstrates how to set up a streaming audio interaction with the Realtime API. The sender continuously streams audio data to the model, while the receivers handle the audio responses and transcripts from the model.

By using these decorators, you can easily define multiple senders and receivers for different types of inputs and outputs (text, audio, streaming audio, etc.) without having to manually manage the complexities of the underlying API calls and WebSocket communication.

### Examples

#### Text-only Interaction

!!! mira ""

    ```python
        import asyncio
        from typing import Any

        from mirascope.beta.openai import Context, Realtime, async_input

        app = Realtime(
            "gpt-4o-realtime-preview-2024-10-01",
            modalities=["text"],
        )


        @app.receiver("text")
        async def receive_text(response: str, context: dict[str, Any]) -> None:
            print(f"AI(text): {response}", flush=True)


        @app.sender(wait_for_text_response=True)
        async def send_message(context: Context) -> str:
            message = await async_input("Enter your message: ")
            return message


        asyncio.run(app.run())
    ```

#### Audio Interaction with Turn Detection

!!! mira ""

    ```python
        import asyncio
        from io import BytesIO

        from typing import AsyncGenerator, Any

        from pydub import AudioSegment
        from pydub.playback import play

        from mirascope.beta.openai import Realtime, record_as_stream

        app = Realtime(
            "gpt-4o-realtime-preview-2024-10-01",
        )


        @app.receiver("audio")
        async def receive_audio(response: AudioSegment, context: dict[str, Any]) -> None:
            play(response)


        @app.receiver("audio_transcript")
        async def receive_audio_transcript(response: str, context: dict[str, Any]) -> None:
            print(f"AI(audio_transcript): {response}")


        @app.sender()
        async def send_audio_as_stream(
            context: dict[str, Any],
        ) -> AsyncGenerator[BytesIO, None]:
            print("Sending audio...")
            async for stream in record_as_stream():
                yield stream


        asyncio.run(app.run())
    ```

#### Audio Interaction without Turn Detection

!!! mira ""

    ```python
        import asyncio
        from io import BytesIO

        from typing import Any

        from pydub import AudioSegment
        from pydub.playback import play

        from mirascope.beta.openai import Realtime, async_input, record

        app = Realtime(
            "gpt-4o-realtime-preview-2024-10-01",
            turn_detection=None,
        )


        @app.receiver("audio")
        async def receive_audio(response: AudioSegment, context: dict[str, Any]) -> None:
            play(response)


        @app.receiver("audio_transcript")
        async def receive_audio_transcript(response: str, context: dict[str, Any]) -> None:
            print(f"AI(audio_transcript): {response}")


        @app.sender(wait_for_audio_transcript_response=True)
        async def send_audio(context: dict[str, Any]) -> BytesIO:
            message = await async_input(
                "Press Enter to start recording or enter exit to shutdown app"
            )
            if message == "exit":
                raise asyncio.CancelledError

            async def wait_for_enter() -> str:
                return await async_input("Press Enter to stop recording...")

            recorded_audio = await record(custom_blocking_event=wait_for_enter)
            return recorded_audio


        asyncio.run(app.run())
    ```

#### Streaming Audio Interaction without Turn Detection

!!! mira ""

    ```python
        import asyncio
        from io import BytesIO

        from typing import AsyncGenerator, Any

        from pydub import AudioSegment
        from pydub.playback import play

        from mirascope.beta.openai import Realtime, record_as_stream, async_input


        app = Realtime(
            "gpt-4o-realtime-preview-2024-10-01",
            turn_detection=None,
        )


        @app.receiver("audio")
        async def receive_audio(response: AudioSegment, context: dict[str, Any]) -> None:
            play(response)


        @app.receiver("audio_transcript")
        async def receive_audio_transcript(response: str, context: dict[str, Any]) -> None:
            print(f"AI(audio_transcript): {response}")


        @app.sender(wait_for_audio_transcript_response=True)
        async def send_audio_as_stream(
            context: dict[str, Any],
        ) -> AsyncGenerator[BytesIO, None]:
            message = await async_input(
                "Press Enter to start recording or enter exit to shutdown app"
            )
            if message == "exit":
                raise asyncio.CancelledError

            async def wait_for_enter() -> str:
                return await async_input("Press Enter to stop recording...")

            async for stream in record_as_stream(custom_blocking_event=wait_for_enter):
                yield stream


        asyncio.run(app.run())
    ```

#### Audio Interaction with Tools and Turn Detection

!!! mira ""

    ```python
        import asyncio
        from io import BytesIO

        from typing import AsyncGenerator, Any

        from pydub import AudioSegment
        from pydub.playback import play

        from mirascope.beta.openai import Realtime, record_as_stream, OpenAIRealtimeTool


        def format_book(title: str, author: str) -> str:
            return f"{title} by {author}"


        app = Realtime("gpt-4o-realtime-preview-2024-10-01", tools=[format_book])


        @app.receiver("audio")
        async def receive_audio(response: AudioSegment, context: dict[str, Any]) -> None:
            play(response)


        @app.receiver("audio_transcript")
        async def receive_audio_transcript(response: str, context: dict[str, Any]) -> None:
            print(f"AI(audio_transcript): {response}")


        @app.sender()
        async def send_audio_as_stream(
            context: dict[str, Any],
        ) -> AsyncGenerator[BytesIO, None]:
            print("Sending audio...")
            async for stream in record_as_stream():
                yield stream


        @app.function_call(format_book)
        async def recommend_book(tool: OpenAIRealtimeTool, context: dict[str, Any]) -> str:
            result = tool.call()
            print(result)
            return result


        asyncio.run(app.run())
    ```

#### Text-only Interaction with Tools

!!! mira ""

    ```python
        import asyncio
        from typing import Any

        from mirascope.beta.openai import Context, Realtime, async_input

        from mirascope.beta.openai import OpenAIRealtimeTool


        def format_book(title: str, author: str) -> str:
            return f"{title} by {author}"


        app = Realtime(
            "gpt-4o-realtime-preview-2024-10-01", modalities=["text"], tools=[format_book]
        )


        @app.sender(wait_for_text_response=True)
        async def send_message(context: Context) -> str:
            genre = await async_input("Enter a genre: ")
            return f"Recommend a {genre} book. please use the tool `format_book`."


        @app.receiver("text")
        async def receive_text(response: str, context: dict[str, Any]) -> None:
            print(f"AI(text): {response}", flush=True)


        @app.function_call(format_book)
        async def recommend_book(tool: OpenAIRealtimeTool, context: Context) -> str:
            result = tool.call()
            return result


        asyncio.run(app.run())
    ```

#### Text-only Interaction with dynamic Tools

!!! mira ""

    ```python
        import asyncio
        from typing import Any, Callable

        from mirascope.beta.openai import Context, Realtime, async_input

        from mirascope.beta.openai import OpenAIRealtimeTool

        app = Realtime(
            "gpt-4o-realtime-preview-2024-10-01",
            modalities=["text"],
        )


        def format_book(title: str, author: str) -> str:
            return f"{title} by {author}"


        @app.sender(wait_for_text_response=True)
        async def send_message(context: Context) -> tuple[str, list[Callable]]:
            genre = await async_input("Enter a genre: ")
            return f"Recommend a {genre} book. please use the tool `format_book`.", [
                format_book
            ]


        @app.receiver("text")
        async def receive_text(response: str, context: dict[str, Any]) -> None:
            print(f"AI(text): {response}", flush=True)


        @app.function_call(format_book)
        async def recommend_book(tool: OpenAIRealtimeTool, context: Context) -> str:
            result = tool.call()
            print(result)
            return result


        asyncio.run(app.run())
    ```

### Notes

- The Realtime API is currently in beta, and its API may change in future releases.
- Make sure to handle exceptions and cancellation appropriately in your senders and receivers.
- The examples provided use the `pydub` library for audio playback. You may need to install additional dependencies for audio support.
- [FFmpeg](https://www.ffmpeg.org/) is required for audio processing. Make sure to install FFmpeg on your system before using the audio features of Mirascope's OpenAI Realtime API support.
