from mirascope.core import prompt_template, vertex


@vertex.call("gemini-1.5-flash", response_model=list[str])
@prompt_template("Extract book titles from {texts}")
def extract_book(texts: list[str]): ...


book = extract_book(
    [
        "The Name of the Wind by Patrick Rothfuss",
        "Mistborn: The Final Empire by Brandon Sanderson",
    ]
)
print(book)
# Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
