from dataclasses import dataclass

from mirascope import llm


@llm.prompt_template(spec="Please recommend a book")
def simple_prompt_template(): ...


@llm.prompt_template(spec="Please recommend a {{ genre }} book")
def genre_prompt_template(genre: str): ...


@dataclass
class Book:
    title: str
    author: str


@llm.prompt_template("Recommend a book like {{ book.title }} by {{ book.author }}.")
def book_prompt_template(book: Book): ...


@llm.prompt_template(
    """
    Please recommend a {{ genre }} book.
    Include the title, author, and a brief description.
    Format your response as a numbered list.
    """
)
def multiline_template(genre: str): ...


# BAD - inconsistent indentation
@llm.prompt_template(
    """
    [USER] First line
    Second line with different indentation
    """
)
def bad_indentation_template(): ...


# GOOD - consistent indentation
@llm.prompt_template(
    """
    [USER]
    First line
    Second line with same indentation
    """
)
def good_indentation_template(): ...
