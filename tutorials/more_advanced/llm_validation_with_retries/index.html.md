# LLM Validation With Retries

This recipe demonstrates how to leverage Large Language Models (LLMs) -- specifically Anthropic's Claude 3.5 Sonnet -- to perform automated validation on any value. We'll cover how to use **LLMs for complex validation tasks**, how to integrate this with Pydantic's validation system, and how to leverage [Tenacity](https://tenacity.readthedocs.io/en/latest/) to automatically **reinsert validation errors** back into an LLM call to **improve results**.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/response_models/">Response Model</a></li>
<li><a href="../../../learn/retries/">Tenacity Integration</a></li>
</ul>
</div>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p>
While traditional validation tools like type checkers or Pydantic are limited to hardcoded rules (such as variable types or arithmetic), LLMs allow for much more nuanced and complex validation. This approach can be particularly useful for validating natural language inputs or complex data structures where traditional rule-based validation falls short.
</p>
</div>

## Setup

Let's start by installing Mirascope and its dependencies:


```python
!pip install "mirascope[anthropic,tenacity]"
```


```python
import os

os.environ["ANTHROPIC_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Basic LLM Validation

Let's start with a simple example of using an LLM to check for spelling and grammatical errors in a text snippet:


```python
from mirascope.core import anthropic, prompt_template
from pydantic import BaseModel, Field


class SpellingAndGrammarCheck(BaseModel):
    has_errors: bool = Field(
        description="Whether the text has typos or grammatical errors"
    )


@anthropic.call(
    model="claude-3-5-sonnet-20240620",
    response_model=SpellingAndGrammarCheck,
    json_mode=True,
)
@prompt_template(
    """
    Does the following text have any typos or grammatical errors? {text}
    """
)
def check_for_errors(text: str): ...


text = "Yestday I had a gret time!"
response = check_for_errors(text)
assert response.has_errors
```


## Pydantic's AfterValidator

We can use Pydantic's [`AfterValidator`](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.AfterValidator) to integrate our LLM-based validation directly into a Pydantic model:



```python
from typing import Annotated

from mirascope.core import anthropic, prompt_template
from pydantic import AfterValidator, BaseModel, ValidationError


@anthropic.call(
    model="claude-3-5-sonnet-20240620",
    response_model=SpellingAndGrammarCheck,
    json_mode=True,
)
@prompt_template(
    """
    Does the following text have any typos or grammatical errors? {text}
    """
)
def check_for_errors(text: str): ...


class TextWithoutErrors(BaseModel):
    text: Annotated[
        str,
        AfterValidator(
            lambda t: t
            if not (check_for_errors(t)).has_errors
            else (_ for _ in ()).throw(ValueError("Text contains errors"))
        ),
    ]


valid = TextWithoutErrors(text="This is a perfectly written sentence.")

try:
    invalid = TextWithoutErrors(
        text="I walkd to supermarket and i picked up some fish?"
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

    Validation error: 1 validation error for TextWithoutErrors
    text
      Value error, Text contains errors [type=value_error, input_value='I walkd to supermarket a... i picked up some fish?', input_type=str]
        For further information visit https://errors.pydantic.dev/2.8/v/value_error



## Reinsert Validation Errors For Improved Performance

One powerful technique for enhancing LLM generations is to automatically reinsert validation errors into subsequent calls. This approach allows the LLM to learn from its previous mistakes as few-shot examples and improve it's output in real-time. We can achieve this using Mirascope's integration with Tenacity, which collects `ValidationError` messages for easy insertion into the prompt.



```python
from typing import Annotated

from mirascope.core import anthropic, prompt_template
from mirascope.integrations.tenacity import collect_errors
from pydantic import AfterValidator, BaseModel, Field, ValidationError
from tenacity import retry, stop_after_attempt


class SpellingAndGrammarCheck(BaseModel):
    has_errors: bool = Field(
        description="Whether the text has typos or grammatical errors"
    )


@anthropic.call(
    model="claude-3-5-sonnet-20240620",
    response_model=SpellingAndGrammarCheck,
    json_mode=True,
)
@prompt_template(
    """
    Does the following text have any typos or grammatical errors? {text}
    """
)
def check_for_errors(text: str): ...


class GrammarCheck(BaseModel):
    text: Annotated[
        str,
        AfterValidator(
            lambda t: t
            if not (check_for_errors(t)).has_errors
            else (_ for _ in ()).throw(ValueError("Text still contains errors"))
        ),
    ] = Field(description="The corrected text with proper grammar")
    explanation: str = Field(description="Explanation of the corrections made")


@retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
@anthropic.call(
    "claude-3-5-sonnet-20240620", response_model=GrammarCheck, json_mode=True
)
@prompt_template(
    """
    {previous_errors}

    Correct the grammar in the following text.
    If no corrections are needed, return the original text.
    Provide an explanation of any corrections made.

    Text: {text}
    """
)
def correct_grammar(
    text: str, *, errors: list[ValidationError] | None = None
) -> anthropic.AnthropicDynamicConfig:
    previous_errors = f"Previous Errors: {errors}" if errors else "No previous errors."
    return {"computed_fields": {"previous_errors": previous_errors}}


try:
    text = "I has went to the store yesterday and buyed some milk."
    result = correct_grammar(text)
    print(f"Corrected text: {result.text}")
    print(f"Explanation: {result.explanation}")
except ValidationError:
    print("Failed to correct grammar after 3 attempts")
```

    Corrected text: I went to the store yesterday and bought some milk.
    Explanation: The sentence has been corrected as follows: 'has went' was changed to 'went' (simple past tense of 'go'), and 'buyed' was changed to 'bought' (past tense of 'buy'). The subject-verb agreement was also fixed by changing 'I has' to 'I'.


<div class="admonition tip">
<p class="admonition-title">Additional Real-World Examples</p>
<ul>
<li><b>Code Review</b>: Validate code snippets for best practices and potential bugs.</li>
<li><b>Data Quality Checks</b>: Validate complex data structures for consistency and completeness.</li>
<li><b>Legal Document Validation</b>: Check legal documents for compliance with specific regulations.</li>
<li><b>Medical Record Validation</b>: Ensure medical records are complete and consistent.</li>
<li><b>Financial Report Validation</b>: Verify financial reports for accuracy and compliance with accounting standards.</li>
</ul>
</div>


When adapting this recipe to your specific use-case, consider the following:

- Tailor the prompts to provide clear instructions and relevant context for your specific validation tasks.
- Balance the trade-off between validation accuracy and performance, especially when implementing retries.
- Implement proper error handling and logging for production use.
- Consider caching validation results for frequently validated items to improve performance.

