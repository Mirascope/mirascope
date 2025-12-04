from dotenv import load_dotenv

from mirascope import llm

load_dotenv()


@llm.call("openai/gpt-5", thinking=True)
def count_primes() -> str:
    return "How many primes below 200 have 79 as a substring? Answer ONLY with the number of primes, not the primes themselves."


response = count_primes()
print(response.pretty())

with llm.model("openai/gpt-5", thinking=False):
    response = response.resume(
        "If you remember the primes, list them. Or say 'I dont remember'"
    )
print(response.pretty())
