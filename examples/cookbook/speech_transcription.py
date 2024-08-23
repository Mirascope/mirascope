import os
from typing import Literal

from dotenv import load_dotenv
from google.generativeai import configure
from pydantic import BaseModel, Field

from mirascope.core import gemini, prompt_template

load_dotenv()
configure(api_key=os.environ["GEMINI_API_KEY"])

apollo_url = "https://storage.googleapis.com/generativeai-downloads/data/Apollo-11_Day-01-Highlights-10s.mp3"


@gemini.call(model="gemini-1.5-flash")
@prompt_template(
    """
    Transcribe the content of this speech:
    {url:audio}
    """
)
def transcribe_speech_from_url(url: str): ...


response = transcribe_speech_from_url(apollo_url)

print(response)


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


response = analyze_audio(apollo_url)
print(response)


with open("YOUR_MP3_HERE", "rb") as file:
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
