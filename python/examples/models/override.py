from mirascope import llm


def ask_question(question: str) -> llm.Response:
    model = llm.use_model("openai/gpt-4o")
    return model.call(question)


# Uses the default model (gpt-4o)
response = ask_question("What is 2 + 2?")

# Override with a different model at runtime
with llm.model("anthropic/claude-sonnet-4-5"):
    response = ask_question("What is 2 + 2?")  # Uses Claude instead
