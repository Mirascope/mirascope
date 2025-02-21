from mirascope import BaseDynamicConfig, BaseMessageParam, prompt_template


@prompt_template()
def recommend_book_prompt(genre: str) -> BaseDynamicConfig:
    uppercase_genre = genre.upper()
    messages = [
        BaseMessageParam(role="user", content=f"Recommend a {uppercase_genre} book")
    ]
    return {
        "messages": messages,
        "computed_fields": {"uppercase_genre": uppercase_genre},
    }


print(recommend_book_prompt("fantasy"))
print(recommend_book_prompt("fantasy"))
# Output: {
#     "messages": [BaseMessageParam(role="user", content="Recommend a FANTASY book")],
#     "computed_fields": {"uppercase_genre": "FANTASY"},
# }
