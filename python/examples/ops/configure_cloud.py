from mirascope import ops

# Configure Mirascope Cloud (uses MIRASCOPE_API_KEY env var)
ops.configure()

# Or pass the API key directly:
# ops.configure(api_key="your-api-key")

# Now all traced operations will be sent to Mirascope Cloud
