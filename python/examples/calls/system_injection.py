from mirascope import llm


# Unsafe - Do not do this!
def unsafe_recommendation(genre: str):
    return [
        llm.messages.system(f"You are a librarian who recommends books in {genre}."),
        llm.messages.user("Please recommend a book!"),
    ]
