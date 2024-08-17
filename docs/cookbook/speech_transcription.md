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
import os

from google.generativeai import configure

from mirascope.core import gemini, prompt_template

configure(api_key=os.environ["GEMINI_API_KEY"])


@gemini.call(model="gemini-1.5-flash")
@prompt_template(
    """
    Transcribe the content of this speech:
    {url:audio}
    """
)
def transcribe_speech_from_url(url: str): ...


response = transcribe_speech_from_url(
    "https://storage.googleapis.com/generativeai-downloads/data/Apollo-11_Day-01-Highlights-10s.mp3"
)
print(response)
# > T minus 10 nine eight We have a go for main engine start We have main engine start
```

## Tagging audio 

We can start by creating a Pydantic Model with the content we want to analyze:

```python
from typing import Literal

from pydantic import BaseModel, Field


class AudioTag(BaseModel):
    audio_quality: Literal["Low", "Medium", "High"] = Field(
        ...,
        description="""The quality of the audio file.
        Low - unlistenable due to severe static, distortion, or other imperfections
        Medium - Audible but noticeable imperfections
        High - crystal clear sound""",
    )
    imperfections: list[str] = Field(
        ...,
        description="""A list of the imperfections affecting audio quality, if any.
        Common imperfections are static, distortion, background noise, echo, but include
        all that apply, even if not listed here""",
    )
    description: str = Field(
        ..., description="A one sentence description of the audio content"
    )
    primary_sound: str = Field(
        ...,
        description="""A quick description of the main sound in the audio,
        e.g. `Male Voice`, `Cymbals`, `Rainfall`""",
    )
```

Now we make our call passing in our `AudioTag` into the `response_model` field:

```python
@gemini.call(model="gemini-1.5-flash", response_model=AudioTag, json_mode=True)
@prompt_template(
    """
    Analyze this audio file
    {url:audio}

    Give me its audio quality (low, medium, high), a list of its audio flaws (if any),
    a quick description of the content of the audio, and the primary sound in the audio.
    Use the tool call passed into the API call to fill it out.
    """
)
def analyze_audio(url: str): ...
response = analyze_audio(
    "https://storage.googleapis.com/generativeai-downloads/data/Apollo-11_Day-01-Highlights-10s.mp3"
)
print(response)
# > audio_quality='Medium' imperfections=['Background Noise'] description='A countdown from 10 to 0 with a voice that says, "We have a go for main engine start." ' primary_sound='Male Voice'
```

## Speaker Diarization

Now let's look at an audio file with multiple people talking. For the purposes of this recipe, I grabbed a snippet from Creative Commons[https://www.youtube.com/watch?v=v0l-u0ZUOSI], around 1:15 in the video and giving Gemini the audio file.

```python
with open("YOUR_MP3_FILE", "rb") as file:
    data = file.read()

    @gemini.call(model="gemini-1.5-flash")
    @prompt_template(
        """
        Transcribe the content of this speech adding speaker tags 
        for example: 
            Person 1: hello 
            Person 2: good morning
        
        
        {data:audio}
        """
    )
    def transcribe_speech_from_file(data: bytes): ...

    response = transcribe_speech_from_file(data)
    print(response)
# Person 1: Good morning. 
# Person 2: Good morning everyone.
# Person 1:  Um, this is our uh wonderful uh legal Q&R Q&A session. I'm I'm sorry. I've I've lost my link to the notes document, so I'm I'm I'm not going to have the formal introduction.  I I can introduce myself. I'm I'm I know who I am most of the time.  
# Person 2: That's good. Why not? Um,
# Person 1: Let's see. So, I think Well, so welcome everyone. I'm sorry I'm a little flustered. I was I I had trouble getting into the room, and so Um, uh, welcome everyone. We We We We have the This is a wonderful opportunity as part of this course to um get to ask questions to some of the most amazing legal minds and who are wonderfully uh friendly and helpful and non-scary um and um We just are uh our privilege to talk to Mari-Jacob who is an amazing uh legal scholar and and uh speaker and and communicator. And I think um the plan will be that we have We have a document which have questions but which has questions that people have been putting in, but I think um it's also people who've been able to be here. Have we started the recording by the way?
# Person 2: Yep. 
# Person 3: Rebecca? 
# Person 2: Yes.  Okay. Good. Good. So, just to warn people everyone we are recording, but um um 
# Person 1:  So, that we have a a document with questions and um, but we'd like to prioritize anyone who's here as well. So, I think maybe um, I will just hand it over to P
```

!!! tip "Additional Real-World Examples"
    - **Subtitles and Closed Captions**: Automatically generate subtitles for same and different languages for accessibility.
    - **Meetings**: Transcribe meetings for future reference or summarization.
    - **Voice Assistant**: Transcription is the first step to answering voice requests.

When adapting this recipe to your specific use-case, consider the following:

- Split your audio file into multiple chunks and run the transcription in parallel.
- Compare results with traditional machine learning techniques.
- Experiment with the prompt by giving it some context before asking to transcribe the audio.
