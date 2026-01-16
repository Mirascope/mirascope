from mirascope import llm

model = llm.model("openai/gpt-5-mini")


def summarize(text: str):
    return model.call(f"Summarize this text in one line: \n{text}")


def translate(text: str, language: str):
    return model.call(f"Translate this text to {language}: \n{text}")


text = """
To be, or not to be, that is the question:
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take arms against a sea of troubles
And by opposing end them.
"""

summary = summarize(text)
print(f"Summary: {summary.text()}")

translation = translate(summary.text(), "french")
print(f"Translation: {translation.text()}")
