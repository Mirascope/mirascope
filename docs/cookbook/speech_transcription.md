# Transcribing Speech

In this recipe, we go over how to transcribe the speech from an audio file using Gemini 1.5 Flash’s audio capabilities.

??? tip "Mirascope Concepts Used"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)
    - [Response Model](../learn/response_models.md)

!!! note "Background"

    LLMs have significantly advanced speech transcription beyond traditional machine learning techniques, by improved handling of diverse accents and languages, and the ability to incorporate context for more precise transcriptions. Additionally, LLMs can leverage feedback loops to continuously improve their performance and correct errors through simple prompting.

## Transcribing Speech using Gemini

With Gemini’s multimodal capabilities, audio input is treated just like text input, which means we can use it as context to ask questions. We will use an audio clip provided by Google of [a countdown of the Apollo Launch](https://storage.googleapis.com/generativeai-downloads/data/Apollo-11_Day-01-Highlights-10s.mp3). Note that if you use your own URL, Gemini currently has a byte limit of `20971520` when not using their file system.

Since we can treat the audio like any other text context, we can create a transcription simply by inserting the audio into the prompt and asking for a transcription:

```python
--8<-- "examples/cookbook/speech_transcription.py:1:1"
--8<-- "examples/cookbook/speech_transcription.py:3:5"
--8<-- "examples/cookbook/speech_transcription.py:9:30"
```

## Tagging audio 

We can start by creating a Pydantic Model with the content we want to analyze:

```python
--8<-- "examples/cookbook/speech_transcription.py:2:3"
--8<-- "examples/cookbook/speech_transcription.py:6:7"
--8<-- "examples/cookbook/speech_transcription.py:31:53"
```

Now we make our call passing in our `AudioTag` into the `response_model` field:

```python
--8<-- "examples/cookbook/speech_transcription.py:56:73"
```

## Speaker Diarization

Now let's look at an audio file with multiple people talking. For the purposes of this recipe, I grabbed a snippet from Creative Commons[https://www.youtube.com/watch?v=v0l-u0ZUOSI], around 1:15 in the video and giving Gemini the audio file.

```python
--8<-- "examples/cookbook/speech_transcription.py:75:105"
```

!!! tip "Additional Real-World Examples"
    - **Subtitles and Closed Captions**: Automatically generate subtitles for same and different languages for accessibility.
    - **Meetings**: Transcribe meetings for future reference or summarization.
    - **Voice Assistant**: Transcription is the first step to answering voice requests.

When adapting this recipe to your specific use-case, consider the following:

- Split your audio file into multiple chunks and run the transcription in parallel.
- Compare results with traditional machine learning techniques.
- Experiment with the prompt by giving it some context before asking to transcribe the audio.
