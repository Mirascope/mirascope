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
--8<-- "examples/cookbook/pii_scrubbing.py:1:17"
--8<-- "examples/cookbook/pii_scrubbing.py:25:46"
```

Using Mirascope’s `response_model` we first detect if PII exists and return a `bool` , this will determine our next steps.

## Verify the prompt quality

We will be using a fake document to test the accuracy of our prompt:

```python
--8<-- "examples/cookbook/pii_scrubbing.py:19:22"
--8<-- "examples/cookbook/pii_scrubbing.py:69:73"
```

## Redact PII

For articles that are flagged as containing PII, we now need to redact that information if we are still planning on sending that document. We create another prompt specific to redacting data by provide an example for the LLM to use:

```python
--8<-- "examples/cookbook/pii_scrubbing.py:49:84"
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
