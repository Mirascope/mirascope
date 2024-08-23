from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini", json_mode=True)
@prompt_template(
    """
    Provide the following information about {book_title}:
    - author
    - date published
    - genre
    """
)
def get_book_info(book_title: str): ...


response = get_book_info("The Great Gatsby")
print(response.content)
