from mirascope import llm

msg = llm.Message(role="user", content="Hi! What's 2+2?")
reply = llm.Message(role="assistant", content="Hi back! 2+2 is 4.")

system_msg = llm.system("You are a helpful librarian who recommends books.")
user_msg = llm.user("Can you recommend a good fantasy book?")
assistant_msg = llm.assistant("I recommend 'The Name of the Wind' by Patrick Rothfuss.")

system_msg = llm.Message(
    role="system", content="You are a librarian who gives concise book recommendations."
)
user_msg = llm.Message(role="user", content="Can you recommend a good fantasy book?")
assistant_msg = llm.Message(
    role="assistant", content="Consider 'The Name of the Wind' by Patrick Rothfuss."
)

conversation = [
    llm.system("You are a helpful cooking assistant."),
    llm.user("How do I make scrambled eggs?"),
    llm.assistant("Here's how to make perfect scrambled eggs..."),
]
