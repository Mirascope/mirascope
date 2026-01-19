from mirascope import llm

# Register a general provider for all anthropic/ models
llm.register_provider("anthropic", api_key="default-key")

# Register a specific provider for one model (longest match wins)
llm.register_provider(
    "anthropic", scope="anthropic/claude-sonnet-4-5", api_key="sonnet-key"
)

# This uses "default-key"
haiku = llm.use_model("anthropic/claude-haiku-4-5")

# This uses "sonnet-key" (more specific scope wins)
sonnet = llm.use_model("anthropic/claude-sonnet-4-5")
