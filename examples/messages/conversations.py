from mirascope import llm

single_query = [
    llm.messages.user("What's the capital of France?"),
]

multi_turn = [
    llm.messages.system("You are a helpful librarian."),
    llm.messages.user("I need a book recommendation."),
    llm.messages.assistant("I'd be happy to help! What genre interests you?"),
    llm.messages.user("I like science fiction."),
    llm.messages.assistant("Want a classic? Check out Dune by Frank Herbert."),
]

multi_participant = [
    llm.messages.user("I need help finding research materials"),
    llm.messages.assistant(
        "I can help you get started. What's your research topic?", name="ConciergeAgent"
    ),
    llm.messages.user("I'm researching climate change impacts on agriculture"),
    llm.messages.assistant(
        "For academic sources on climate and agriculture, I recommend starting with...",
        name="LibrarianAgent",
    ),
]
