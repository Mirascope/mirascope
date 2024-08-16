from openai import OpenAI

from mirascope.core import openai, prompt_template

PII_DEFINITION = """
Any representation of information that permits the identity of an individual to whom 
the information applies to be reasonably inferred by either direct or indirect means. 
Further, PII is defined as information: (i) that directly identifies an 
individual (e.g., name, address, social security number or other identifying 
number or code, telephone number, email address, etc.) or (ii) by which an agency 
intends to identify specific individuals in conjunction with other data elements, 
i.e., indirect identification. (These data elements may include a combination of gender, 
race, birth date, geographic indicator, and other descriptors). Additionally, 
information permitting the physical or online contacting of a specific individual is 
the same as personally identifiable information. This information can be maintained 
in either paper, electronic or other media.
"""

PII_ARTICLE = """
John Doe, born on 12/07/1985, resides at 123 Ruecker Harbor in Goodwinshire, WI. 
His Social Security number is 325-21-4386 and he can be reached at (123) 456-7890. 
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


def run():
    does_pii_exist = check_if_pii_exists(PII_ARTICLE)
    if does_pii_exist:
        return scrub_pii(PII_ARTICLE)
    else:
        return "No PII found in the article."


print(run())
