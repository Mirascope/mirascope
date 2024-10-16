# Realtime API (Beta)

Mirascope's Realtime API provides a simple and intuitive way to leverage [OpenAI's cutting-edge Realtime API](https://platform.openai.com/docs/guides/realtime). This integration allows developers to easily create dynamic, interactive applications with real-time audio and text capabilities, all while abstracting away the complexities of WebSocket management and event handling.

With Mirascope, you can quickly set up and use advanced features of OpenAI's Realtime API without dealing with low-level WebSocket operations or complex event structures. This allows you to focus on building your application logic rather than worrying about the intricacies of API communication.

!!! warning "Beta Feature"
    The Realtime API integration is currently in beta. As such, the interface is subject to change in future releases. We recommend using this feature with caution in production environments and staying updated with the latest documentation and releases.

## Key Features

Mirascope's Realtime API wrapper offers a range of powerful features that make it easy to build sophisticated real-time applications:

- **Audio Input/Output**: Seamlessly handle both audio input from users and audio output from the model, enabling natural voice interactions.
- **Audio Stream Input**: Support for streaming audio input, allowing for real-time processing of continuous audio data.
- **Text Input/Output**: Easily manage text-based interactions alongside audio, providing flexibility in communication modes.
- **Audio Transcript Output**: Automatically receive transcripts of audio outputs, useful for logging, display, or further processing.
- **Multi-modal Interactions**: Combine audio and text modalities in the same session for rich, flexible user experiences.
- **Simplified Session Management**: Abstract away the complexities of WebSocket connections and session handling.
- **Easy-to-use Decorator Pattern**: Utilize intuitive Python decorators to define senders and receivers, streamlining your code structure.
- **Asynchronous Support**: Built-in support for asynchronous operations, allowing for efficient handling of I/O-bound tasks.

These features enable developers to create a wide range of applications, from voice assistants and interactive chatbots to complex multi-modal AI systems, all while leveraging the power of OpenAI's latest models through a clean, Pythonic interface.


## Basic Usage

To use the `Realtime` class, create an instance with the desired model and configure senders and receivers for handling input and output. Mirascope uses Python decorators to simplify the process of defining senders and receivers.

Here's a complete example demonstrating how to set up a streaming audio interaction:

```python
--8<-- "examples/beta/openai/realtime/audio_stream_input_output.py"
```

Let's break down the key components of this example:

1. First, we create a `Realtime` instance with the specified model:
    ```python
    --8<-- "examples/beta/openai/realtime/audio_stream_input_output.py:10:13"
    ```
2. We define two receivers using the `@app.receiver` decorator:
    ```python
    --8<-- "examples/beta/openai/realtime/audio_stream_input_output.py:16:25"
    ```
    The first receiver handles audio responses by playing them, while the second receiver prints the audio transcript.
3. We define a sender using the `@app.sender` decorator:
    ```python
    --8<-- "examples/beta/openai/realtime/audio_stream_input_output.py:27:32"
    ```
   This sender function streams audio data to the model using the `record_as_stream()` function.
4. Finally, we run the application:
    ```python
    --8<-- "examples/beta/openai/realtime/audio_stream_input_output.py:35"
    ```

This example demonstrates how to set up a streaming audio interaction with the Realtime API. The sender continuously streams audio data to the model, while the receivers handle the audio responses and transcripts from the model.

By using these decorators, you can easily define multiple senders and receivers for different types of inputs and outputs (text, audio, streaming audio, etc.) without having to manually manage the complexities of the underlying API calls and WebSocket communication.

## Examples

### Text-only Interaction

```python
--8<-- "examples/beta/openai/realtime/text_input_output.py"
```

### Audio Interaction without Turn Detection

```python
--8<-- "examples/beta/openai/realtime/audio_input_output_manually.py"
```

### Streaming Audio Interaction without Turn Detection

```python
--8<-- "examples/beta/openai/realtime/audio_stream_input_output_manually.py"
```

## Notes

- The Realtime API is currently in beta, and its API may change in future releases.
- Make sure to handle exceptions and cancellation appropriately in your senders and receivers.
- The examples provided use the `pydub` library for audio playback. You may need to install additional dependencies for audio support.
- [FFmpeg](https://www.ffmpeg.org/) is required for audio processing. Make sure to install FFmpeg on your system before using the audio features of the Realtime API.