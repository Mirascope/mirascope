from mirascope import llm


@llm.call("google/gemini-3-pro", thinking={"level": "high", "include_thoughts": True})
def solve(problem: str) -> str:
    return problem


response = solve("What is the first prime number that contains 42 as a substring?")
print(response.pretty())
