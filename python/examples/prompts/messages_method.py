from mirascope import llm


@llm.prompt
def recommend_book(genre: str):
    return f"Please recommend a book in {genre}."


# Get the messages without calling the LLM
messages = recommend_book.messages("fantasy")
print(messages)
# [UserMessage(content=[Text(text='Please recommend a book in fantasy.')])]
