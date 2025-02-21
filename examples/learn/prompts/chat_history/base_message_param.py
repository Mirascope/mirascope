from mirascope import BaseMessageParam, prompt_template


@prompt_template()
def chatbot(query: str, history: list[BaseMessageParam]) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(role="system", content="You are a librarian"),
        *history,
        BaseMessageParam(role="user", content=query),
    ]


history = [
    BaseMessageParam(role="user", content="Recommend a book"),
    BaseMessageParam(role="assistant", content="What genre do you like?"),
]
print(chatbot("fantasy", history))
# Output: [
#     BaseMessageParam(role="system", content="You are a librarian"),
#     BaseMessageParam(role="user", content="Recommend a book"),
#     BaseMessageParam(role="assistant", content="What genre do you like?"),
#     BaseMessageParam(role="user", content="fantasy"),
# ]
