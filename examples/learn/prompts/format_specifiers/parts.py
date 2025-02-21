from mirascope import TextPart, prompt_template


@prompt_template(
    """
    Book themes:
    {themes:text}

    Character analysis:
    {characters:texts}
    """
)
def analyze_book(themes: TextPart, characters: list[TextPart]): ...


prompt = analyze_book(
    themes=TextPart(type="text", text="redemption, power, friendship"),
    characters=[
        TextPart(type="text", text="Name: Frodo, Role: Protagonist"),
        TextPart(type="text", text="Name: Gandalf, Role: Mentor"),
    ],
)

print(prompt[0].content)
# Output:
# [
#     TextPart(type="text", text="Book themes:"),
#     TextPart(type="text", text="redemption, power, friendship"),
#     TextPart(type="text", text="Character analysis:"),
#     TextPart(type="text", text="Name: Frodo, Role: Protagonist"),
#     TextPart(type="text", text="Name: Gandalf, Role: Mentor"),
# ]
