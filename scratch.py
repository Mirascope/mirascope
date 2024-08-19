import asyncio

from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template("{query}")
def call(query: str): ...


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
@prompt_template("Concisely answer the following question: {query}")
async def answer(query: str): ...


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Here is the original query:
    {query}

    Here is an initial response to the query:
    {response}

    Here is some fact checking on the response:
    {verification_q_and_a}

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
        f"Q:{q}\nA:{a}" for q, a in zip(verification_questions, verification_answers)
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

print(asyncio.run(chain_of_verification(query=query)))
