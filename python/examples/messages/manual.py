from mirascope import llm

message = llm.UserMessage(content=[llm.Text(type="text", text="Hi! What's 2+2?")])
reply = llm.AssistantMessage(content=[llm.Text(type="text", text="Hi back! 2+2 is 4.")])

system_message = llm.SystemMessage(
    content=llm.Text(
        type="text", text="You are a librarian who gives concise book recommendations."
    ),
)
user_message = llm.UserMessage(
    role="user",
    content=[llm.Text(type="text", text="Can you recommend a good fantasy book?")],
)
assistant_message = llm.AssistantMessage(
    content=[
        llm.Text(
            type="text", text="Consider 'The Name of the Wind' by Patrick Rothfuss."
        )
    ],
)
