# Transcribing Speech

In this recipe, we go over how to transcribe the speech from an audio file using Gemini 1.5 Flash’s audio capabilities.

??? info "Key Concepts"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)

!!! note "Background"

    LLMs have significantly advanced speech transcription beyond traditional machine learning techniques, by improved handling of diverse accents and languages, and the ability to incorporate context for more precise transcriptions. Additionally, LLMs can leverage feedback loops to continuously improve their performance and correct errors through simple prompting.

## Transcribing Speech using Gemini

With Gemini’s multimodal capabilities, audio input is treated just like text input, which means we can use it as context to ask questions. We will use an audio clip provided by Google of [a countdown of the Apollo Launch](https://storage.googleapis.com/generativeai-downloads/data/Apollo-11_Day-01-Highlights-10s.mp3). Note that if you use your own URL, Gemini currently has a byte limit of `20971520` when not using their file system.

Since we can treat the audio like any other text context, we can create a transcription simply by inserting the audio into the prompt and asking for a transcription:

```python
import os

from google.generativeai import configure

from mirascope.core import gemini, prompt_template

configure(api_key=os.environ["GEMINI_API_KEY"])


@gemini.call(model="gemini-1.5-flash")
@prompt_template(
    """
    Transcribe the content of this speech:
    {audio:url}
    """
)
def transcribe_speech(url: str): ...


response = transcribe_speech(
    "https://storage.googleapis.com/generativeai-downloads/data/Apollo-11_Day-01-Highlights-10s.mp3"
)
print(response)
# > T minus 10 nine eight We have a go for main engine start We have main engine start
```

!!! tip "Additional Real-World Examples"
    - **Subtitles and Closed Captions**: Automatically generate subtitles for same and different languages for accessibility.
    - **Meetings**: Transcribe meetings for future reference or summarization.
    - **Voice Assistant**: Transcription is the first step to answering voice requests.

When adapting this recipe to your specific use-case, consider the following:

- Split your audio file into multiple chunks and run the transcription in parallel.
- Compare results with traditional machine learning techniques.
