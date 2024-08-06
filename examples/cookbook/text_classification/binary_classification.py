from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini", response_model=bool)
@prompt_template("Classify the following text as spam or not spam: {text}")
def classify_spam(text: str): ...


text = "Would you like to buy some cheap viagra?"
label = classify_spam(text)
assert label is True  # This text is classified as spam

text = "Hi! It was great meeting you today. Let's stay in touch!"
label = classify_spam(text)
assert label is False  # This text is classified as not spam
