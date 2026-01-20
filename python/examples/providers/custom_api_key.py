from mirascope import llm

# Use a different API key for OpenAI
llm.register_provider("openai", api_key="sk-my-other-key")

# Or point to a different endpoint (e.g., a proxy)
llm.register_provider("openai", base_url="https://my-proxy.example.com/v1")

# Now all openai/ calls use the registered configuration
response = llm.use_model("openai/gpt-4o-mini").call("Say hello")
print(response.text())
