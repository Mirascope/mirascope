# Chain of Verification: Enhancing LLM Accuracy through Self-Verification

This recipe demonstrates how to implement the Chain of Verification technique using Large Language Models (LLMs) with Mirascope. Chain of Verification is a prompt engineering method that enhances an LLM's accuracy by generating and answering verification questions based on its initial response.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../../learn/calls/">Calls</a></li>
<li><a href="../../../../learn/response_models/">Response Models</a></li>
</ul>
</div>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p>
<a href="https://arxiv.org/pdf/2309.11495">Chain of Verification</a> is a prompt engineering technique where one takes a prompt and its initial LLM response then generates a checklist of questions that can be used to verify the initial answer. Each of these questions are then answered individually with separate LLM calls, and the results of each verification question are used to edit the final answer. LLMs are often more truthful when asked to verify a particular fact rather than use it in their own answer, so this technique is effective in reducing hallucinations.
</p>
</div>


## Implementation

Let's implement the Chain of Verification technique using Mirascope:







```python
import asyncio

from mirascope.core import openai, prompt_template
from pydantic import BaseModel, Field


@openai.call("gpt-4o-mini")
def call(query: str) -> str:
    return query


class VerificationQuestions(BaseModel):
    questions: list[str] = Field(
        ...,
        description="""A list of questions that verifies if the response
        answers the original query correctly.""",
    )


@openai.call("gpt-4o-mini", response_model=VerificationQuestions)
@prompt_template(
    """
    SYSTEM:
    You will be given a query and a response to the query.
    Take the relevant statements in the response and rephrase them into questions so
    that they can be used to verify that they satisfy the original query.
    USER:
    Query:
    {query}

    Response:
    {response}
    """
)
def get_verification_questions(query: str, response: str): ...


@openai.call("gpt-4o-mini")
async def answer(query: str) -> str:
    return f"Concisely answer the following question: {query}"


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Here is the original query:
    {query}

    Here is an initial response to the query:
    {response}

    Here is some fact checking on the response:
    {verification_q_and_a:list}

    Using the knowledge you learned from verification, re-answer the original query.
    """
)
async def cov_call(query: str) -> openai.OpenAIDynamicConfig:
    response = call(query).content
    verification_questions = get_verification_questions(query, response).questions
    tasks = [answer(question) for question in verification_questions]
    responses = await asyncio.gather(*tasks)
    verification_answers = [response.content for response in responses]
    verification_q_and_a = [
        [f"Q:{q}", f"A:{a}"]
        for q, a in zip(verification_questions, verification_answers)
    ]
    return {
        "computed_fields": {
            "response": response,
            "verification_q_and_a": verification_q_and_a,
        }
    }


async def chain_of_verification(query: str):
    response = await cov_call(query=query)
    # Uncomment to see intermediate responses
    # print(response.user_message_param["content"])
    return response


query = "Name 5 politicians born in New York."

print(await chain_of_verification(query=query))
```

    Here are five politicians who were born in New York:
    
    1. **Theodore Roosevelt** - 26th President of the United States, born in New York City, New York.
    2. **Al Smith** - Governor of New York and Democratic presidential candidate, born in New York City, New York.
    3. **Andrew Cuomo** - Former Governor of New York, born in Queens, New York City.
    4. **Franklin D. Roosevelt** - 32nd President of the United States, born in Hyde Park, New York.
    5. **Donald Trump** - 45th President of the United States, born in Queens, New York City.
    
    These individuals have all made significant contributions to American politics and governance. Note that Hillary Clinton, while a prominent politician, was actually born in Chicago, Illinois.


As we can see, the Chain of Verification process has successfully identified and corrected an error in the initial response (Hillary Clinton's birthplace), demonstrating its effectiveness in improving accuracy.

## Benefits and Considerations

The Chain of Verification implementation offers several advantages:

1. Improved accuracy by systematically verifying initial responses.
2. Reduction of hallucinations and factual errors in LLM outputs.
3. Transparent fact-checking process that can be easily audited.

When implementing this technique, consider:

- Balancing the number of verification questions with response time and computational cost.
- Tailoring the verification question generation process to your specific use case.
- Implementing error handling for cases where verification reveals significant discrepancies.

When adapting this recipe to your specific use-case, consider:

- Customizing the verification question generation process for your domain.
- Implementing a feedback loop to continuously improve the verification process based on user feedback or expert review.
- Combining Chain of Verification with other techniques like Chain of Thought for even more robust reasoning capabilities.
- Experimenting with different LLM models for various stages of the verification process to optimize for accuracy and efficiency.

By leveraging Mirascope's `call` decorator, response models, and dynamic configuration, you can easily implement and customize the Chain of Verification technique to enhance your LLM's accuracy across a wide range of applications.

