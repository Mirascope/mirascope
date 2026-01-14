from mirascope import llm

# System messages set context and instructions
system_message = llm.messages.system(
    "You are a friendly librarian who helps find books."
)

# User messages are input from the person using the LLM
user_message = llm.messages.user("Can you recommend a mystery novel?")

# Assistant messages represent LLM responses (usually from prior interactions)
assistant_message = llm.messages.assistant(
    "I'd recommend 'The Silent Patient' by Alex Michaelides!",
    model_id=None,
    provider_id=None,
)
