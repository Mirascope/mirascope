from mirascope import llm

message = llm.UserMessage(content=[("Hi! What's 2+2?")])
reply = llm.AssistantMessage(content=[("Hi back! 2+2 is 4.")])

system_message = llm.SystemMessage(
    content="You are a librarian who gives concise book recommendations.",
)
user_message = llm.UserMessage(
    role="user", content=[("Can you recommend a good fantasy book?")]
)
assistant_message = llm.AssistantMessage(
    content=[("Consider 'The Name of the Wind' by Patrick Rothfuss.")],
)
