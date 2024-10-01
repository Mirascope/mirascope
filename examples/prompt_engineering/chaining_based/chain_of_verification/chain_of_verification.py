import asyncio

from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template("{query}")
def call(query: str): ...


class VerificationQuestions(BaseModel):
    questions: list[str] = Field(
        ...,
        description="""A list of questions that  verifies if the response
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
        f"Q:{q}\nA:{a}"
        for q, a in zip(verification_questions, verification_answers, strict=False)
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
# > Here are five politicians who were born in New York:
#
#   1. **Franklin D. Roosevelt** - 32nd President of the United States, born in Hyde Park, New York.
#   2. **Theodore Roosevelt** - 26th President of the United States, born in New York City.
#   3. **Andrew Cuomo** - Former Governor of New York, born in Queens, New York City.
#   4. **Chuck Schumer** - U.S. Senator from New York and Senate Majority Leader, born in Brooklyn, New York City.
#   5. **Kirsten Gillibrand** - U.S. Senator from New York, born in Albany, New York.
#
#   These individuals have been influential figures in American politics. Note that Hillary Clinton was incorrectly listed as being born in New York; she was born in Chicago, Illinois.


# Intermediate Responses:

# aggregate prompt for cov call:
# Here is the original query:
# Name 5 politicians born in New York.

# Here is an initial response to the query:
# Here are five politicians who were born in New York:

# 1. Franklin D. Roosevelt - 32nd President of the United States.
# 2. Theodore Roosevelt - 26th President of the United States.
# 3. Hillary Clinton - Former U.S. Senator and Secretary of State.
# 4. Andrew Cuomo - Former Governor of New York.
# 5. Chuck Schumer - U.S. Senator from New York and Senate Majority Leader.

# These individuals have played significant roles in American politics.

# Here is some fact checking on the response:
# ['Q:Who is Franklin D. Roosevelt and where was he born?\nA:Franklin D. Roosevelt was the 32nd President of the United States, serving from 1933 to 1945. He was born in Hyde Park, New York.', 'Q:Who is Theodore Roosevelt and where was he born?\nA:Theodore Roosevelt was the 26th President of the United States, serving from 1901 to 1909. He was born in New York City on October 27, 1858.', 'Q:Who is Hillary Clinton and where was she born?\nA:Hillary Clinton is an American politician, lawyer, and diplomat who served as the Secretary of State from 2009 to 2013 and was the Democratic nominee for President in 2016. She was born in Chicago, Illinois.', 'Q:Who is Andrew Cuomo and where was he born?\nA:Andrew Cuomo is an American politician who served as the Governor of New York from 2011 to 2021. He was born in Queens, New York City.', 'Q:Who is Chuck Schumer and where was he born?\nA:Chuck Schumer is an American politician serving as the Senate Majority Leader and a U.S. Senator from New York. He was born in Brooklyn, New York City.']

# Using the knowledge you learned from verification, re-answer the original query.
