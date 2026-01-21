from mirascope import llm

# Use a more capable model for nuanced summarization
summarizer = llm.model("openai/gpt-5")
# Use a faster model for straightforward translation
translator = llm.model("openai/gpt-5-mini")


def summarize(text: str):
    return summarizer.call(f"Summarize this text: {text}")


def translate(text: str, language: str):
    return translator.call(f"Translate this text to {language}: {text}")


def summarize_and_translate(text: str, language: str) -> str:
    summary = summarize(text)
    return translate(summary.text(), language).text()


text = """
What a piece of work is a man! how noble in reason!
how infinite in faculty! in form and moving how
express and admirable! in action how like an angel!
in apprehension how like a god! the beauty of the
world! the paragon of animals! And yet, to me,
what is this quintessence of dust?
"""

translation = summarize_and_translate(text, "french")
print(translation)
