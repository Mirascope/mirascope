import os


def load_api_key() -> str:
    """Load the API key from the standard environment variable."""
    return os.environ.get("MISTRAL_API_KEY", "")
