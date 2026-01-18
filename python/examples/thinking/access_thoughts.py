from mirascope import llm


@llm.call(
    "anthropic/claude-sonnet-4-5",
    thinking={"level": "medium", "include_thoughts": True},
)
def solve(problem: str) -> str:
    return problem


response = solve("How many primes below 100 contain 7 as a digit?")

for thought in response.thoughts:
    print(f"Thought: {thought.thought}")

print(f"Answer: {response.texts[0].text}")
