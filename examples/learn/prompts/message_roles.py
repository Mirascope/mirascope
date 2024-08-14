from mirascope.core import BasePrompt, prompt_template


@prompt_template(
    """
    SYSTEM: You are the world's greatest librarian
    USER: Recommend a {genre} book
    """
)
class RecommendBookPrompt(BasePrompt):
    genre: str


prompt = RecommendBookPrompt(genre="fantasy")
print(prompt)
# > SYSTEM: You are the world's greatest librarian
#   USER: Recommend a fantasy book
print(prompt.message_params())
# > [BaseMessageParam(role='system', content="You are the world's greatest librarian"), BaseMessageParam(role='user', content='Recommend a fantasy book')]
