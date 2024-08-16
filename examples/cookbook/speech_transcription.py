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
