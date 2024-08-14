from mirascope.core import BasePrompt, prompt_template


@prompt_template(
    """
    SYSTEM: You are the world's greatest librarian.
    USER: {query}
    """
)
class BookRecommendationPrompt(BasePrompt):
    query: str | None


prompt = BookRecommendationPrompt(query=None)
print(prompt.message_params())
# >[BaseMessageParam(role='system', content="You are the world's greatest librarian.")]
