from mirascope import llm


@llm.call(
    "anthropic/claude-sonnet-4-5",
    thinking={"level": "high", "include_thoughts": True},
)
def solve(problem: str) -> str:
    return problem


response = solve("Prove that the square root of 2 is irrational.")
print(response.pretty())
