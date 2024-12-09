# Text Translation

This guide introduces advanced techniques for translating from English to Japanese. Due to significant differences in their origins, grammatical structures, and cultural backgrounds, generating natural Japanese through mechanical translation is extremely challenging. The methods presented here are applicable not only to English-Japanese translation but also to translation between any structurally different languages.

We will explore innovative approaches to improve translation quality using Large Language Models (LLMs). Specifically, we will introduce three techniques:

1. Parametrized Translation
2. Multi-Pass Translation
3. Multi-Provider Translation

These techniques can be applied to various LLMs, including OpenAI's GPT-4, Anthropic's Claude, and Google's Gemini.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/response_models/">Response Models</a></li>
</ul>
</div>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p>
Translation between English and Japanese presents several unique challenges:
</p>
<ol>
<li><b>Context Dependency</b>: Japanese is a high-context language where much information is conveyed implicitly.</li>
<li><b>Grammatical Structure Differences</b>: Japanese follows an SOV structure, while English follows an SVO structure.</li>
<li><b>Subject Handling</b>: In Japanese, it's common to omit the subject when it's clear from context.</li>
<li><b>Honorifics and Polite Expressions</b>: Japanese has multiple levels of honorifics that need to be appropriately chosen based on social context.</li>
<li><b>Idiomatic Expressions and Cultural Nuances</b>: Both languages have unique idioms and culturally rooted expressions.</li>
</ol>
</div>


## Setup

Let's start by installing Mirascope and its dependencies:


```python
!pip install "mirascope[openai, anthropic, gemini]" 
```


```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
os.environ["ANTHROPIC_API_KEY"] = "YOUR_API_KEY"
os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Translation Techniques Leveraging LLMs

### Parametrized Translation

Parametrized translation introduces parameters such as tone and target audience into the translation process to generate more appropriate and context-aware translations.


```python
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
prompt_translation = prompt.translate(call=openai.call, model="gpt-4o-mini")

# In Jupyter Notebook, use the following code to run async functions:
parametrized_translation = await prompt_translation

# In Python script, use the following code:
# parametrized_translation = asyncio.run(prompt_translation)

print(f"Parametrized with translation: {parametrized_translation}")
```

    Parametrized with translation: その老いぼれは、本当に根性のある人だったが、自分の夢のビジネスアイデアを実現させようと、無理をして頑張り続けていた。何ヶ月も無駄に過ごし、出来の悪いマーケティング計画に手をこまねいて、全く的外れな努力をしていた。



This technique allows translators to adjust translations according to the target audience and required tone.

### Multi-Pass Translation

Multi-Pass translation involves repeating the same translation process multiple times, evaluating and improving the translation at each pass.



```python
from collections.abc import Callable
from contextlib import contextmanager
from enum import StrEnum

from mirascope.core import BasePrompt, openai, prompt_template
from pydantic import BaseModel, Field


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


multi_pass_translation_task = multi_pass_translation(
    text,
    tone=Tone.casual,
    audience=Audience.general,
    pass_count=3,
    call=openai.call,
    model="gpt-4o-mini",
)

# In Jupyter Notebook, use the following code to run async functions:
multi_pass_result = await multi_pass_translation_task

# In Python script, use the following code:
# multi_pass_result = asyncio.run(multi_pass_translation

print(f"Multi-pass translation result: {multi_pass_result}")
```

    model='gpt-4o-mini' Multi-pass translation start times: 1
    model='gpt-4o-mini' Multi-pass translation end times: 1
    model='gpt-4o-mini' Multi-pass translation start times: 2
    model='gpt-4o-mini' Multi-pass translation end times: 2
    model='gpt-4o-mini' Multi-pass translation start times: 3
    model='gpt-4o-mini' Multi-pass translation end times: 3
    Multi-pass translation result: そのおじいさんは、ほんとうの自力で成功を目指して、昼も夜も頑張っていたんだ。夢のようなビジネスアイデアを実現しようと奮闘していたけど、何ヶ月も無駄に時間を使っていただけだったんだ。ちょっと変なマーケティングプランに手を出しちゃって、完全に間違った道に進んでいたんだよ。



This technique allows for gradual improvement in various aspects such as grammar, vocabulary, and style, resulting in more natural and accurate translations.


### Multi-Provider Translation

Multi-Provider translation involves using multiple LLM providers in parallel and comparing their results.

Install the required other provider's dependencies using the following command:


```python
!pip install ipywidgets # for Jupyter Notebook
```


```python
from collections.abc import Callable
from contextlib import contextmanager
from enum import StrEnum

from mirascope.core import BasePrompt, anthropic, gemini, openai, prompt_template
from pydantic import BaseModel, Field


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


text = """
The old codger, a real bootstrapper, had been burning the candle at both ends trying to make his pie-in-the-sky business idea fly. He'd been spinning his wheels for months, barking up the wrong tree with his half-baked marketing schemes.
"""


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


multi_provider_translation_task = multi_provider_translation(
    text,
    tone=Tone.professional,
    audience=Audience.academic,
    pass_count=2,
    call_models=[
        (openai.call, "gpt-4o-mini"),
        (anthropic.call, "claude-3-5-sonnet-20240620"),
        (gemini.call, "gemini-1.5-flash"),
    ],
)

# In Jupyter Notebook, use the following code to run async functions:
await multi_provider_translation_task

# In Python script, use the following code:
# asyncio.run(multi_provider_translation_task)
```

    model='gpt-4o-mini' Multi-pass translation start times: 1
    model='claude-3-5-sonnet-20240620' Multi-pass translation start times: 1
    model='gemini-1.5-flash' Multi-pass translation start times: 1
    model='gemini-1.5-flash' Multi-pass translation end times: 1
    model='gemini-1.5-flash' Multi-pass translation start times: 2
    model='gpt-4o-mini' Multi-pass translation end times: 1
    model='gpt-4o-mini' Multi-pass translation start times: 2
    model='gemini-1.5-flash' Multi-pass translation end times: 2
    model='claude-3-5-sonnet-20240620' Multi-pass translation end times: 1
    model='claude-3-5-sonnet-20240620' Multi-pass translation start times: 2
    model='gpt-4o-mini' Multi-pass translation end times: 2
    model='claude-3-5-sonnet-20240620' Multi-pass translation end times: 2
    Translations:
    Model: gpt-4o-mini, Translation: その年配の男性は、本当の自力で成り上がった人物であり、夢のビジネスアイデアを実現するために徹夜で努力していました。しかし、彼は何ヶ月も無駄にし、未熟なマーケティング戦略で誤った方向に進んでいました。
    Model: claude-3-5-sonnet-20240620, Translation: 高齢の実業家は、真の独立自営者として、非現実的なビジネス構想の実現に向けて昼夜を問わず懸命に努力していた。数ヶ月にわたり、彼は効果的な進展を見せることなく時間を費やし、不十分な準備状態のマーケティング戦略を用いて誤った方向性に労力を注いでいた。この状況は、彼の努力が必ずしも適切な方向に向けられていなかったことを示唆している。
    Model: gemini-1.5-flash, Translation: その老人は、自力で成功しようと、実現不可能な夢のようなビジネスアイデアに固執し、夜遅くまで働き詰めでした。彼は、行き当たりばったりのマーケティング戦略で何ヶ月も無駄な努力を重ねてきました。 
    


This method allows for comparison of translation results from different models, enabling the selection of the most appropriate translation.

## Conclusion

The techniques demonstrated in this recipe can help to significantly improve the quality and efficiency of English-Japanese translation through parametrization, multi-pass, and multi-provider techniques. By combining these methods, it effectively handles complex translation tasks and flexibly addresses diverse translation needs.
