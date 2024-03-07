from mirascope.openai import OpenAIPrompt


class p(OpenAIPrompt):
    """{greeting}."""

    greeting: str


prompt = p(
    greeting="Hello", api_key="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"
)
print(prompt.dump(), "\n")
comp = prompt.create()
print(comp.dump(), "\n")
print(prompt.dump(), "\n")
print(prompt._start_time, prompt._end_time)
