# Prompt Paraphrasing: Generating Diverse Prompts for LLM Testing and Evaluation

[Prompt Paraphrasing](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00324/96460/How-Can-We-Know-What-Language-Models-Know) is not a prompt engineering technique, but rather a prompt generation technique used to create ensembles of prompts for testing or other prompt engineering techniques. In this example, we cover a specific method of generating prompts mentioned in the paper whereby a prompt is translated into $B$ versions in another language, then backtranslated into $B^2$ versions to English.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../../learn/calls/">Calls</a></li>
<li><a href="../../../../learn/response_models/">Response Models</a></li>
</ul>
</div>

## Implementation

Let's implement the Prompt Paraphrasing technique using Mirascope:





```python
from mirascope.core import openai, prompt_template
from pydantic import BaseModel, Field


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


def prompt_paraphrasing(query: str, num_translations: int = 3) -> set[str]:
    spanish_translations = translate(
        phrase=query,
        language="Spanish",
        num_translations=num_translations,
    )
    # Avoid Duplicates
    prompt_variations = set()
    for spanish_phrase in spanish_translations.translations:
        back_translations = translate(
            spanish_phrase, language="English", num_translations=3
        )
        prompt_variations.update(back_translations.translations)
    return prompt_variations


print(
    prompt_paraphrasing(
        query="What are some manageable ways to improve my focus and productivity?"
    )
)
```

    {'What are some ways to boost my focus and achieve greater productivity in a manageable fashion?', 'How can I improve my focus and productivity?', 'What methods are effective for enhancing my concentration and productivity?', 'What are some practical strategies to boost my focus and productivity?', 'What are some feasible methods to enhance my concentration and productivity?', 'What are some manageable ways to improve my focus and productivity?', 'What are useful ways to increase my concentration and productivity?', 'How can I improve my focus and be more productive in a manageable way?', 'How can I enhance my concentration and increase my productivity in a sustainable manner?'}



This implementation consists of two main functions:

1. `translate`: This function takes a phrase, target language, and number of translations as input, and returns multiple translations of the phrase in the specified language.
2. `prompt_paraphrasing`: This function orchestrates the Prompt Paraphrasing technique. It first translates the input query into Spanish, then back-translates each Spanish translation into English, creating a set of diverse prompt variations.

## Benefits and Considerations

The Prompt Paraphrasing implementation offers several advantages:

1. Generation of diverse prompt variations for more robust LLM testing and evaluation.
2. Potential discovery of more effective phrasings for specific tasks or queries.
3. Improved understanding of LLM behavior across different linguistic formulations.

When implementing this technique, consider:

- Balancing the number of translations and languages with computational cost and time constraints.
- Selecting appropriate languages for translation based on your specific use case or target audience.
- Implementing a filtering mechanism to remove nonsensical or overly divergent paraphrases.

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Robustness Testing</b>: Use prompt paraphrasing to test LLM performance across various phrasings of the same query.</li>
<li><b>Data Augmentation</b>: Generate additional training data by paraphrasing existing prompts or questions.</li>
<li><b>Chatbot Improvement</b>: Enhance chatbot understanding by training on paraphrased versions of common queries.</li>
<li><b>Cross-lingual Information Retrieval</b>: Improve search results by querying with multiple paraphrased versions of the search term.</li>
<li><b>Writing Assistance</b>: Offer users alternative phrasings for their writing to improve clarity or style.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider:

- Experimenting with different source and target languages for translation.
- Implementing a scoring mechanism to rank paraphrases based on relevance or quality.
- Combining Prompt Paraphrasing with other techniques like Chain of Thought or Self-Consistency for more comprehensive LLM evaluation.
- Developing a feedback loop to refine the paraphrasing process based on LLM performance on different prompt variations.

By leveraging Mirascope calls and response models, you can easily implement and customize the Prompt Paraphrasing technique to generate diverse prompts for LLM testing, evaluation, and improvement across a wide range of applications.


