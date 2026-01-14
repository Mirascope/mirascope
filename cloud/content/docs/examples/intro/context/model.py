from mirascope import llm


class Library:
    available_books: list[str]
    detailed_book_info: dict[str, str]


@llm.tool()
# [!code highlight:2]
def get_book_info(ctx: llm.Context[Library], book: str) -> str:
    return ctx.deps.detailed_book_info.get(book, "Book not found")


# [!code highlight:2]
def librarian(ctx: llm.Context[Library], query: str):
    model = llm.use_model("openai/gpt-5")
    book_list = "\n".join(ctx.deps.available_books)
    messages = [
        llm.messages.system(
            f"You are a librarian, with access to these books: ${book_list}"
        ),
        llm.messages.user(query),
    ]
    # [!code highlight:2]
    return model.context_call(ctx=ctx, messages=messages, tools=[get_book_info])


def main():
    query = "Please recommend a mind-bending book from the library."
    ctx = llm.Context(deps=Library())  # [!code highlight]
    response: llm.ContextResponse[Library] = librarian(ctx, query)  # [!code highlight]

    while response.tool_calls:
        tool_outputs = response.execute_tools(ctx)  # [!code highlight]
        response = response.resume(ctx, tool_outputs)  # [!code highlight]

    print(response.pretty())


main()
