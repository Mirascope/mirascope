from mirascope.experimental.v2 import llm


@llm.call("anthropic:claude-3-5-sonnet-latest")
def answer_question(question: str) -> str:
    return f"Answer this question: ${question}"


response: llm.Response = answer_question("What is the capital of France?")
print(response.text)
