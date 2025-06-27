from mirascope import llm


@llm.prompt_template(
    """
    [SYSTEM] You are a summarization agent. Your job is to summarize long discussions.
    [MESSAGES] {{ history }}
    [USER] Please summarize our conversation, and recommend a book based on this chat.
    """
)
def history_prompt_template(history: list[llm.Message]): ...


with open("book_recommendation.txt") as f:
    template_content = f.read()


@llm.prompt_template(template_content)
def file_based_prompt_template(genre: str): ...
