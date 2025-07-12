

# TODO: Add support for async tools!
# @llm.tool()
async def available_books() -> list[str]:
    """List the available books in the library."""
    return ["Mistborn", "Gödel, Escher, Bach", "Dune"]
