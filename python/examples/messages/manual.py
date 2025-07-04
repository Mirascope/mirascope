from mirascope import llm

message = llm.Message(role="user", content=llm.Text(text="Hi! What's 2+2?"))
reply = llm.Message(role="assistant", content=llm.Text(text="Hi back! 2+2 is 4."))

system_message = llm.Message(
    role="system",
    content=llm.Text(
        text="You are a librarian who gives concise book recommendations."
    ),
)
user_message = llm.Message(
    role="user", content=llm.Text(text="Can you recommend a good fantasy book?")
)
assistant_message = llm.Message(
    role="assistant",
    content=llm.Text(text="Consider 'The Name of the Wind' by Patrick Rothfuss."),
)
