from mirascope import llm

one_shot: llm.Prompt = [
    llm.messages.user("What's a good book to read?"),
]

system_and_user: llm.Prompt = [
    llm.messages.system(
        "You are a librarian, who recommends contemporary young-adult fantasy novels."
    ),
    llm.messages.user("What's a good book to read?"),
]

multi_turn: llm.Prompt = [
    llm.messages.system(
        "You are a librarian, who recommends contemporary young-adult fantasy novels."
    ),
    llm.messages.user("What's a good book to read?"),
    llm.messages.assistant("I recommend Name of the Wind, by Patrick Rothfuss"),
    llm.messages.user(
        "I've already read it! Can you suggest something else with magic and music?"
    ),
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
