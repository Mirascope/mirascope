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
