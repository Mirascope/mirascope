from mirascope import llm

system_message = llm.messages.system(
    "You are a helpful librarian who recommends books."
)
user_message = llm.messages.user("Can you recommend a good fantasy book?")
assistant_message = llm.messages.assistant(
    "I recommend 'The Name of the Wind' by Patrick Rothfuss."
)
