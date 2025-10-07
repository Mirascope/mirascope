from dotenv import load_dotenv

from mirascope import llm

load_dotenv()


@llm.call(provider="openai:responses", model_id="gpt-5", thinking=True)
def count_primes() -> str:
    return "How many primes below 400 have 79 as a substring?"


print("... starting stream ...")
stream = count_primes.stream()
for chunk in stream.pretty_stream():
    print(chunk, flush=True, end="")

stream = stream.resume(
    "Does your current context window include how you got that result? Answer YES or NO."
)
for chunk in stream.pretty_stream():
    print(chunk, flush=True, end="")
