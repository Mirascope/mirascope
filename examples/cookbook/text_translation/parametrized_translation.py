import asyncio
from collections.abc import Callable
from enum import StrEnum

from mirascope.core import BasePrompt, openai, prompt_template


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


@prompt_template(
    """
    SYSTEM:
    You are a professional translator who is a native Japanese speaker.
    Translate the English text into natural Japanese without changing the content.
    Please make sure that the text is easy to read for everyone by using appropriate paragraphs so that it does not become difficult to read.

    Please consider the following parameters in your translation:

    tone: {tone}
    The tone can be one of the following:
    - neutral: Maintain a balanced and impartial tone
    - positive: Use upbeat and optimistic language
    - negative: Convey a more critical or pessimistic view
    - professional: Use formal and business-appropriate language
    - casual: Use informal, conversational language

    audience: {audience}
    The audience can be one of the following:
    - general: For the general public, use common terms and clear explanations
    - professional: For industry professionals, use appropriate jargon and technical terms
    - academic: For scholarly contexts, use formal language and cite sources if necessary
    - friendly: For casual, familiar contexts, use warm and approachable language
    - formal: For official or ceremonial contexts, use polite and respectful language

    Adjust your translation style based on the specified tone and audience to ensure the message is conveyed appropriately.

    USER:
    text: {text}
    """
)
class ParametrizedTranslatePrompt(BasePrompt):
    tone: Tone
    audience: Audience
    text: str

    async def translate(self, call: Callable, model: str) -> str:
        response = await self.run_async(call(model))
        return response.content


text = """
The old codger, a real bootstrapper, had been burning the candle at both ends trying to make his pie-in-the-sky business idea fly. He'd been spinning his wheels for months, barking up the wrong tree with his half-baked marketing schemes.
"""
prompt = ParametrizedTranslatePrompt(
    text=text, tone=Tone.negative, audience=Audience.general
)
parametrized_translation = asyncio.run(
    prompt.translate(call=openai.call, model="gpt-4o-mini")
)
print(f"Parametrized with translation: {parametrized_translation}")
