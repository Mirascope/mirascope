from mirascope import llm


@llm.call(
    "anthropic/claude-sonnet-4-5",
    thinking={"level": "medium", "include_thoughts": True},
)
def analyze(question: str) -> str:
    return question


response = analyze("List the first 10 prime numbers.")

# Resume with a different provider, encoding thoughts as text
# so the new model can read the prior reasoning
with llm.model(
    "openai/gpt-5-mini",
    thinking={"level": "none", "encode_thoughts_as_text": True},
):
    followup = response.resume("What's the sum of those primes?")

print(followup.pretty())
