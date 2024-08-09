from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template


class Translations(BaseModel):
    translations: list[str] = Field(
        ..., description="The list of translations into the requested language"
    )


@openai.call(model="gpt-4o-mini", response_model=Translations)
@prompt_template(
    """
    For this phrase: {phrase}


    Give {num_translations} translations in {language}
    """
)
def translate(phrase: str, language: str, num_translations: int): ...


def prompt_paraphrasing(query: str, num_translations: int = 3):
    spanish_translations = translate(
        phrase=query,
        language="Spanish",
        num_translations=num_translations,
    )
    # Uncomment to see intermediate responses
    print(spanish_translations)
    # Avoid Duplicates
    prompt_varations = set()
    for spanish_phrase in spanish_translations.translations:
        back_translations = translate(
            spanish_phrase, language="English", num_translations=3
        )
        prompt_varations.update(back_translations.translations)
    return prompt_varations


print(
    prompt_paraphrasing(
        query="What are some manageable ways to improve my focus and productivity?"
    )
)
# > {'What are some manageable ways to improve my focus and productivity?', 'What manageable ways are there to improve my focus and productivity?', 'How can I improve my focus and productivity in a manageable way?', 'Which are some manageable ways to boost my focus and productivity?', 'What can I do to boost my focus and productivity in a manageable fashion?', 'What manageable methods are there to boost my focus and productivity?', 'Which manageable forms are there to enhance my focus and productivity?', 'How can I enhance my focus and productivity in a manageable manner?', 'What are some practical ways to enhance my focus and productivity?'}


# Intermediate Responses
# spanish translations
# > ['¿Cuáles son algunas maneras manejables de mejorar mi enfoque y productividad?', '¿Qué formas manejables hay para mejorar mi enfoque y productividad?', '¿Cómo puedo mejorar mi enfoque y productividad de manera manejable?']
