from mirascope import llm

# Message names for multi-user scenarios
user_alice = llm.user("What's the weather like today?", name="Alice")
user_bob = llm.user("I'm also curious about the forecast.", name="Bob")
assistant_weather = llm.assistant(
    "It's currently sunny and 75°F with clear skies expected all day.",
    name="WeatherBot",
)
assistant_travel = llm.assistant(
    "Perfect weather for outdoor activities!", name="TravelBot"
)

# Document content (advanced content type)
document = llm.Document(data="/path/to/research-paper.pdf", mime_type="application/pdf")
document_msg = llm.user(["Please summarize this research paper:", document])

# Tool interactions - when AI calls external functions
tool_call_msg = llm.assistant(
    [
        llm.ToolCall(
            id="call_weather_123",
            name="get_current_weather",
            args={"location": "San Francisco, CA"},
        )
    ]
)

tool_output_msg = llm.user(
    [
        llm.ToolOutput(
            id="call_weather_123",
            value={"temperature": 72, "condition": "sunny", "humidity": 45},
        )
    ]
)

# Thinking content - model's reasoning process
thinking_msg = llm.assistant(
    [
        llm.Thinking(
            id="thinking_book_rec",
            thoughts="The user liked The Martian and Project Hail Mary, both hard sci-fi with problem-solving. They want similar themes but different settings. I should recommend books with clever protagonists facing technical challenges...",
            redacted=False,
        ),
        "Based on your love for Andy Weir's problem-solving narratives, I recommend 'Recursion' by Blake Crouch.",
    ]
)


# Dynamic message construction
def build_conversation(user_preferences, conversation_history):
    messages = [
        llm.system(
            f"You are a helpful assistant specializing in {user_preferences['domain']}."
        ),
    ]

    # Add conversation history
    messages.extend(conversation_history)

    return messages


# Example usage of dynamic construction
user_prefs = {"domain": "book recommendations"}
history = [llm.user("I need a good book to read.")]
dynamic_conversation = build_conversation(user_prefs, history)
