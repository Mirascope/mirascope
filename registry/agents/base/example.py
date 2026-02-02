"""Example usage of the Mirascope Registry agent decorator.

This example demonstrates a librarian agent that can look up books and answer
questions about a library using the agentic loop with hooks.

To run this example:
    1. Install the agent from registry: `mirascope registry add agents/base`
    2. Set your OPENAI_API_KEY environment variable
    3. Run: `python example.py`
"""

from dataclasses import dataclass

# Import from the local agent module (after registry install, use: from ai.agents import ...)
from agent import AgentHooks, agent

from mirascope import llm

# =============================================================================
# Define dependencies
# =============================================================================


@dataclass
class Library:
    """The library context with librarian info and book catalog."""

    librarian_on_duty: str
    books: list[str]


# =============================================================================
# Define tools
# =============================================================================


@llm.tool
def get_books(ctx: llm.Context[Library]) -> list[str]:
    """Returns the list of books available in the library.

    Returns:
        A list of book titles available in the library.
    """
    return ctx.deps.books


@llm.tool
def check_availability(ctx: llm.Context[Library], book_title: str) -> str:
    """Check if a specific book is available in the library.

    Args:
        book_title: The title of the book to check.

    Returns:
        A message indicating whether the book is available.
    """
    books_lower = [b.lower() for b in ctx.deps.books]
    if book_title.lower() in books_lower:
        return f"Yes, '{book_title}' is available in our library!"
    return f"Sorry, '{book_title}' is not in our collection."


# =============================================================================
# Define hooks for observability
# =============================================================================


def log_before_call(messages: list[llm.Message], turn: int) -> None:
    """Log before each LLM call."""
    print(f"\n--- Turn {turn + 1}: Sending {len(messages)} messages to LLM ---")


def log_after_call(response: llm.Response, turn: int) -> None:
    """Log after each LLM call."""
    tool_count = len(response.tool_calls) if response.tool_calls else 0
    print(f"--- Turn {turn + 1}: Received response with {tool_count} tool calls ---")
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"    Tool: {tc.name}({tc.arguments})")


def log_tool_execution(
    tool_call: llm.ToolCall,
    output: llm.ToolOutput,
    turn: int,
) -> None:
    """Log after each tool execution."""
    print(f"    Result: {output.result}")


def log_finish(response: llm.Response, total_turns: int, stop_reason: str) -> None:
    """Log when the agent finishes."""
    print(f"\n=== Agent finished after {total_turns + 1} turn(s) ===")
    print(f"Stop reason: {stop_reason}")


# =============================================================================
# Create the agent
# =============================================================================


@agent(
    "openai/gpt-4o-mini",
    tools=[get_books, check_availability],
    max_turns=5,
    hooks=AgentHooks(
        before_call=log_before_call,
        after_call=log_after_call,
        after_tool=log_tool_execution,
        on_finish=log_finish,
    ),
)
def librarian(ctx: llm.Context[Library]):
    """A helpful librarian agent that can answer questions about the library."""
    return f"""You are {ctx.deps.librarian_on_duty}, a friendly and helpful librarian.
You help patrons find books and answer questions about the library's collection.
Be concise but friendly in your responses."""


# =============================================================================
# Main
# =============================================================================


def main():
    # Create the library context
    library = Library(
        librarian_on_duty="Nancy",
        books=[
            "The Name of the Wind",
            "Dune",
            "Foundation",
            "Neuromancer",
            "Snow Crash",
        ],
    )
    ctx = llm.Context(deps=library)

    print("=" * 60)
    print("LIBRARIAN AGENT EXAMPLE")
    print("=" * 60)

    # Example 1: Ask about available books
    print("\n[User]: What books do you have?")
    response = librarian(ctx, "What books do you have?")
    print(f"\n[Librarian]: {response.text()}")

    print("\n" + "-" * 60)

    # Example 2: Check for a specific book
    print("\n[User]: Do you have Dune?")
    response = librarian(ctx, "Do you have Dune?")
    print(f"\n[Librarian]: {response.text()}")

    print("\n" + "-" * 60)

    # Example 3: Ask about a book not in the collection
    print("\n[User]: I'm looking for Harry Potter")
    response = librarian(ctx, "I'm looking for Harry Potter")
    print(f"\n[Librarian]: {response.text()}")


if __name__ == "__main__":
    main()
