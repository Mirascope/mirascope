from mirascope import llm

system_msg = llm.system("You are a helpful librarian who recommends books.")
user_msg = llm.user("Can you recommend a good fantasy book?")
assistant_msg = llm.assistant("I recommend 'The Name of the Wind' by Patrick Rothfuss.")

system_msg = llm.Message(
    role="system", content="You are a helpful librarian who recommends books."
)
user_msg = llm.Message(role="user", content="Can you recommend a good fantasy book?")
assistant_msg = llm.Message(
    role="assistant", content="I recommend 'The Name of the Wind' by Patrick Rothfuss."
)

conversation = [
    llm.system("You are a helpful cooking assistant."),
    llm.user("How do I make scrambled eggs?"),
    llm.assistant("Here's how to make perfect scrambled eggs..."),
]
