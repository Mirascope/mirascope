import asyncio

from openai import APIError

from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini")
@prompt_template("Explain {concept} in simple terms")
async def explain_concept(concept: str): ...


async def main():
    try:
        response = await explain_concept("quantum computing")
        print(response.content)
    except APIError as e:
        print(f"An error occurred: {e}")


asyncio.run(main())
