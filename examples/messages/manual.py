from mirascope import llm

message = llm.Message(role="user", content="Hi! What's 2+2?")
reply = llm.Message(role="assistant", content="Hi back! 2+2 is 4.")

system_message = llm.Message(
    role="system", content="You are a librarian who gives concise book recommendations."
)
user_message = llm.Message(
    role="user", content="Can you recommend a good fantasy book?"
)
assistant_message = llm.Message(
    role="assistant", content="Consider 'The Name of the Wind' by Patrick Rothfuss."
)
