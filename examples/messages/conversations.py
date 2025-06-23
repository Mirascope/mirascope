from mirascope import llm

# Basic conversation structure
conversation = [
    llm.system("You are a helpful cooking assistant."),
    llm.user("I want to make pasta. What ingredients do I need?"),
    llm.assistant(
        "For basic pasta, you'll need pasta, salt, and water. What type of pasta dish are you thinking of?"
    ),
    llm.user("Something with tomatoes and cheese."),
]

# Single exchange pattern
single_exchange = [
    llm.user("What's the capital of France?"),
    llm.assistant("The capital of France is Paris."),
]

# Multi-turn conversation pattern
multi_turn = [
    llm.system("You are a helpful librarian."),
    llm.user("I need a book recommendation."),
    llm.assistant("I'd be happy to help! What genre interests you?"),
    llm.user("I like science fiction."),
    llm.assistant("Great choice! I recommend 'Dune' by Frank Herbert."),
]

# Context building pattern
context_building = [
    llm.system("You are a travel assistant."),
    llm.user("I'm planning a trip to Japan."),
    llm.assistant("Wonderful! When are you planning to visit?"),
    llm.user("Next spring, around March."),
    llm.assistant(
        "Perfect timing for cherry blossom season! How long will you be staying?"
    ),
    llm.user("About two weeks."),
    llm.assistant(
        "Excellent! With two weeks in March, you could see cherry blossoms in different regions..."
    ),
]

# Complete practical example
complete_conversation = [
    llm.system(
        "You are a helpful book recommendation assistant. Ask clarifying questions to provide personalized recommendations."
    ),
    llm.user("I want to read something new but I'm not sure what."),
    llm.assistant(
        "I'd love to help you find your next great read! What are some books or genres you've enjoyed recently?"
    ),
    llm.user("I really liked 'The Martian' and 'Project Hail Mary' by Andy Weir."),
    llm.assistant(
        "Great choices! You seem to enjoy hard science fiction with problem-solving protagonists. Would you like more space-based sci-fi, or are you open to other settings?"
    ),
    llm.user("I'm open to other settings, but I like the problem-solving aspect."),
    llm.assistant(
        "Perfect! Based on your preferences, I recommend 'Klara and the Sun' by Kazuo Ishiguro for a thought-provoking AI perspective, or 'The Midnight Library' by Matt Haig for philosophical problem-solving. Both feature protagonists working through complex challenges."
    ),
    llm.user("The Midnight Library sounds interesting. What's it about?"),
    llm.assistant(
        "'The Midnight Library' follows Nora, who finds herself in a magical library between life and death. Each book represents a different life she could have lived. She must explore these alternate realities to discover what truly makes life worth living. It combines philosophical questions with engaging storytelling - perfect for someone who enjoys thoughtful problem-solving narratives!"
    ),
]
