from dataclasses import dataclass

from mirascope import llm


@dataclass
class Library:
    books: dict[str, str]  # title -> author


@llm.tool
def get_author(ctx: llm.Context[Library], title: str) -> str:
    """Get the author of a book."""
    return ctx.deps.books.get(title, "Book not found")


@llm.prompt(tools=[get_author])
def librarian(ctx: llm.Context[Library], query: str):
    return query


library = Library(books={"Dune": "Frank Herbert", "Neuromancer": "William Gibson"})
ctx = llm.Context(deps=library)
model = llm.use_model("openai/gpt-5-mini")
response = librarian.call(model, ctx, "Who wrote Dune?")

while response.tool_calls:
    tool_outputs = response.execute_tools(ctx)
    response = response.resume(ctx, tool_outputs)

print(response.pretty())
# Dune was written by Frank Herbert.
