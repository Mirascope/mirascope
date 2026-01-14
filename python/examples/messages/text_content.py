from mirascope import llm

# Plain strings are automatically converted to Text content
user_message = llm.messages.user("Hello!")

# You can also explicitly use llm.Text
user_message_explicit = llm.messages.user(llm.Text(text="Hello!"))
