from mirascope import llm

# Creating messages with shorthand functions
system_message = llm.messages.system("You are a helpful assistant.")
user_message = llm.messages.user("Hello, how are you?")

# Messages are used when calling LLMs
messages: list[llm.Message] = [system_message, user_message]
