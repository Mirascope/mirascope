from enum import StrEnum

from mirascope.core import openai, prompt_template


class Audience(StrEnum):
    general = "general"
    professional = "professional"
    academic = "academic"
    friendly = "friendly"
    formal = "formal"


class Tone(StrEnum):
    neutral = "neutral"
    positive = "positive"
    negative = "negative"
    professional = "professional"
    casual = "casual"


@openai.call("gpt-4o-mini")
@prompt_template(
    """
    SYSTEM:
    You are a professional translator who is a native Japanese speaker.
    Translate the English text into natural Japanese without changing the content.
     Please make sure that the text is easy to read for everyone by using appropriate paragraphs so that it does not become difficult to read.
    
    Also, please translate with respect to the following parameters
    
    USER:
    text: {text}
    tone: {tone}
    audience: {audience}
    """
)
def parametrized_translate(text: str, tone: Tone, audience: Audience) -> None: ...


text = """
The old codger, a real bootstrapper, had been burning the candle at both ends trying to make his pie-in-the-sky business idea fly. He'd been spinning his wheels for months, barking up the wrong tree with his half-baked marketing schemes.
"""
parametrized_translation = parametrized_translate(
    text, tone=Tone.negative, audience=Audience.general
)
print(f"Parametrized with translation: {parametrized_translation}")
