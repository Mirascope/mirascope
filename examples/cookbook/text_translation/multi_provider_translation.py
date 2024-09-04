import asyncio
from collections.abc import Callable
from contextlib import contextmanager
from enum import StrEnum

from pydantic import BaseModel, Field

from mirascope.core import BasePrompt, anthropic, gemini, openai, prompt_template


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


class Evaluation(BaseModel):
    clarity: float = Field(
        ..., description="The clarity of the translation, ranging from 0 to 10."
    )
    naturalness: float = Field(
        ..., description="The naturalness of the translation, ranging from 0 to 10."
    )
    consistency: float = Field(
        ..., description="The consistency of the translation, ranging from 0 to 10."
    )
    grammatical_correctness: float = Field(
        ...,
        description="The grammatical correctness of the translation, ranging from 0 to 10.",
    )
    lexical_appropriateness: float = Field(
        ...,
        description="The lexical appropriateness of the translation, ranging from 0 to 10.",
    )
    subject_clarity: float = Field(
        ...,
        description="The clarity of the subject in the translation, ranging from 0 to 10.",
    )
    word_order_naturalness: float = Field(
        ...,
        description="Maintenance of natural Japanese word order (0 to 10). Evaluates whether the English word order is not directly applied.",
    )
    subject_handling: float = Field(
        ...,
        description="Appropriate handling of subjects (0 to 10). Evaluates whether unnecessary subjects are avoided and appropriately omitted.",
    )
    modifier_placement: float = Field(
        ...,
        description="Appropriate placement of modifiers (0 to 10). Evaluates whether natural Japanese modification relationships are maintained.",
    )
    sentence_length_appropriateness: float = Field(
        ...,
        description="Appropriateness of sentence length (0 to 10). Evaluates whether long sentences are properly divided when necessary.",
    )
    context_dependent_expression: float = Field(
        ...,
        description="Appropriateness of context-dependent expressions (0 to 10). Evaluates whether the level of honorifics and politeness is suitable for the target audience and situation.",
    )
    implicit_meaning_preservation: float = Field(
        ...,
        description="Preservation of implicit meanings (0 to 10). Evaluates whether implicit meanings and cultural nuances from the original English text are appropriately conveyed.",
    )


@prompt_template(
    """
    SYSTEM:
    You are a professional translator who is a native Japanese speaker.
    Please evaluate the following translation and provide feedback on how it can be improved.

    USER:
    original_text: {original_text}
    translation_text: {translation_text}
    """
)
class EvaluateTranslationPrompt(BasePrompt):
    original_text: str
    translation_text: str

    async def evaluate(self, call: Callable, model: str) -> Evaluation:
        response = await self.run_async(call(model, response_model=Evaluation))
        return response


@prompt_template("""
    SYSTEM:
    Your task is to improve the quality of a translation from English into Japanese.
    You will be provided with the original text, the translated text, and an evaluation of the translation.
    All evaluation criteria will be scores between 0 and 10.
    
    The translation you are improving was intended to adhere to the desired tone and audience:
    tone: {tone}
    audience: {audience}
    
    You improved translation MUST also adhere to this desired tone and audience.
    
    Output ONLY the improved translation.
    
    USER:
    original text: {original_text}
    translation: {translation_text}
    evaluation: {evaluation}
""")
class ImproveTranslationPrompt(BasePrompt):
    tone: Tone
    audience: Audience
    original_text: str
    translation_text: str
    evaluation: Evaluation

    async def improve_translation(self, call: Callable, model: str) -> str:
        response = await self.run_async(call(model))
        return response.content


text = """
The old codger, a real bootstrapper, had been burning the candle at both ends trying to make his pie-in-the-sky business idea fly. He'd been spinning his wheels for months, barking up the wrong tree with his half-baked marketing schemes.
"""


@contextmanager
def print_progress_message(model: str, count: int):
    print(f"{model=} Multi-pass translation start times: {count}")
    yield
    print(f"{model=} Multi-pass translation end times: {count}")


async def multi_pass_translation(
    original_text: str,
    tone: Tone,
    audience: Audience,
    pass_count: int,
    call: Callable,
    model: str,
) -> str:
    with print_progress_message(model, 1):
        parametrized_translate_prompt = ParametrizedTranslatePrompt(
            text=original_text, tone=tone, audience=audience
        )
        translation_text = await parametrized_translate_prompt.translate(call, model)

    for current_count in range(2, pass_count + 1):
        with print_progress_message(model, current_count):
            evaluate_translation_prompt = EvaluateTranslationPrompt(
                original_text=original_text, translation_text=translation_text
            )
            evaluation = await evaluate_translation_prompt.evaluate(call, model)
            improve_translation_prompt = ImproveTranslationPrompt(
                original_text=original_text,
                translation_text=translation_text,
                tone=tone,
                audience=audience,
                evaluation=evaluation,
            )
            translation_text = await improve_translation_prompt.improve_translation(
                call, model
            )
    return translation_text


async def multi_provider_translation(
    original_text: str,
    tone: Tone,
    audience: Audience,
    pass_count: int,
    call_models: list[tuple[Callable, str]],
) -> None:
    results = []
    for call, model in call_models:
        results.append(
            multi_pass_translation(
                original_text,
                tone,
                audience,
                pass_count,
                call,
                model,
            )
        )
    translations = await asyncio.gather(*results)
    print("Translations:")
    for (_, model), translation_text in zip(call_models, translations, strict=True):
        print(f"Model: {model}, Translation: {translation_text}")


asyncio.run(
    multi_provider_translation(
        text,
        tone=Tone.professional,
        audience=Audience.academic,
        pass_count=3,
        call_models=[
            (openai.call, "gpt-4o-mini"),
            (anthropic.call, "claude-3-5-sonnet-20240620"),
            (gemini.call, "gemini-1.5-flash"),
        ],
    )
)
