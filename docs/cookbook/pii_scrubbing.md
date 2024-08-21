# PII Scrubbing

In this recipe, we go over how to detect Personal Identifiable Information, or PII and redact it from your source. Whether your source is from a database, a document, or spreadsheet, it is important prevent PII from leaving your system. We will be using Ollama for data privacy.

??? tip "Mirascope Concepts Used"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)
    - [Response Model](../learn/response_models.md)

!!! note "Background"

    Prior to Natural Language Processing (NLP) and Named Entity Recognition (NER) techniques, scrubbing or redacting sensitive information was a time-consuming manual task. LLMs have improved on this by being able to understand context surrounding sensitive information.

## Create your prompt

The first step is to grab the definition of PII for our prompt to use. Note that in this example we will be using US Labor Laws so be sure to use your countries definition. We can access the definition [here](https://www.dol.gov/general/ppii).

```python
from mirascope.core import openai, prompt_template

PII_DEFINITION = """Any representation of information that permits the identity of an individual 
to whom the information applies to be reasonably inferred by either direct or indirect means. 
Further, PII is defined as information: 
(i) that directly identifies an individual (e.g., name, address, social security number or other identifying number or code, telephone number, email address, etc.) 
or (ii) by which an agency intends to identify specific individuals in conjunction with other data elements, i.e., indirect identification. 
(These data elements may include a combination of gender, race, birth date, geographic indicator, and other descriptors). 
Additionally, information permitting the physical or online contacting of a specific individual is the same as personally identifiable information. 
This information can be maintained in either paper, electronic or other media.
"""

@openai.call(
    model="llama3.1",
    client=OpenAI(base_url="http://localhost:11434/v1", api_key="ollama"),
    json_mode=True,
    response_model=bool,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert at identifying personally identifiable information (PII).
    Using the following definition of PII, 
    determine if the article contains PII with True or False?

    Definition of PII:
    {PII_DEFINITION}

    USER:
    {article}
    """
)
def check_if_pii_exists(article: str) -> openai.OpenAIDynamicConfig:
    return {"computed_fields": {"PII_DEFINITION": PII_DEFINITION}}
```

Using Mirascope’s `response_model` we first detect if PII exists and return a `bool` , this will determine our next steps.

## Verify the prompt quality

We will be using a fake document to test the accuracy of our prompt:

```python
PII_ARTICLE = """
John Doe, born on 12/07/1985, resides at 123 Ruecker Harbor in Goodwinshire, WI. 
His Social Security number is 325-21-4386 and he can be reached at (123) 456-7890. 
"""

print(check_if_pii_exists(PII_ARTICLE))
# True
```

## Redact PII

For articles that are flagged as containing PII, we now need to redact that information if we are still planning on sending that document. We create another prompt specific to redacting data by provide an example for the LLM to use:

```python
@openai.call(
    model="llama3.1",
    client=OpenAI(base_url="http://localhost:11434/v1", api_key="ollama"),
)
@prompt_template(
    """
    SYSTEM:
    You are an expert at redacting personally identifiable information (PII).
    Replace the PII in the following article with context words.

    If PII exists in the article, replace it with context words. For example, if the
    phone number is 123-456-7890, replace it with [PHONE_NUMBER].

    USER:
    {article}
    """
)
def scrub_pii(article: str): ...

print(scrub_pii(PII_ARTICLE))
# Here's the redacted article:

# John Doe, born on [DATE_OF_BIRTH], resides at a location in [CITY/TOWN]. His [IDENTIFYING_DOCUMENT] number is [NUMBER_SOMEWHERE]. He can be reached at [PHONE_NUMBER].
```

!!! tip "Additional Real-World Applications"

    - **Medical Records**: Iterate on the above recipe and scrub any PII when sharing patient data for research.
    - **Legal Documents**: Court documents and legal filings frequently contain sensitive information that needs to be scrubbed before public release.
    - **Corporate Financial Reports**: Companies may need to scrub proprietary financial data or trade secrets when sharing reports with external auditors or regulators.
    - **Social Media Content Moderation**: Automatically scrub or blur out personal information like phone numbers or addresses posted in public comments.

When adapting this recipe to your specific use-case, consider the following:

    - Use a larger model hosted on prem or in a private location to prevent data leaks.
    - Refine the prompts for specific types of information you want scrubbed.
    - Run the `check_if_pii_exists` call after scrubbing PII to check if all PII has been scrubbed.
