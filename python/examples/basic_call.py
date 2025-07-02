from mirascope import llm


@llm.call("anthropic:claude-3-5-sonnet-latest")
def answer_question(question: str) -> str:
    return f"Answer this question: ${question}"


response: llm.BaseResponse = answer_question("What is the capital of France?")
print(response.text)
