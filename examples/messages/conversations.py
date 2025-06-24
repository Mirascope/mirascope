from mirascope import llm

single_query = [
    llm.user("What's the capital of France?"),
]

multi_turn = [
    llm.system("You are a helpful librarian."),
    llm.user("I need a book recommendation."),
    llm.assistant("I'd be happy to help! What genre interests you?"),
    llm.user("I like science fiction."),
    llm.assistant("Want a classic? Check out Dune by Frank Herbert."),
]

multi_participant = [
    llm.user("I need help finding research materials"),
    llm.assistant(
        "I can help you get started. What's your research topic?", name="ConciergeAgent"
    ),
    llm.user("I'm researching climate change impacts on agriculture"),
    llm.assistant(
        "For academic sources on climate and agriculture, I recommend starting with...",
        name="LibrarianAgent",
    ),
]
