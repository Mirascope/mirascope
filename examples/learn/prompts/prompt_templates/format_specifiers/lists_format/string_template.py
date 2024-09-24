from mirascope.core import prompt_template


@prompt_template(
    """
    Recommend a book from one of the following genres:
    {genres:list}

    Examples:
    {examples:lists}
    """
)
def recommend_book_prompt(genres: list[str], examples: list[list[str]]): ...


prompt = recommend_book_prompt(
    genres=["fantasy", "scifi", "mystery"],
    examples=[
        ["Title: The Name of the Wind", "Author: Patrick Rothfuss"],
        ["Title: Mistborn: The Final Empire", "Author: Brandon Sanderson"],
    ],
)
print(prompt)
# Output: [
#     BaseMessageParam(
#         role="user",
#         content="Recommend a book from one of the following genres:\nfantasy\nscifi\nmystery\n\nExamples:\nTitle: The Name of the Wind\nAuthor: Patrick Rothfuss\n\nTitle: Mistborn: The Final Empire\nAuthor: Brandon Sanderson",
#     )
# ]

print(prompt[0].content)
# Output:
# Recommend a book from one of the following genres:
# fantasy
# scifi
# mystery

# Examples:
# Title: The Name of the Wind
# Author: Patrick Rothfuss

# Title: Mistborn: The Final Empire
# Author: Brandon Sanderson
