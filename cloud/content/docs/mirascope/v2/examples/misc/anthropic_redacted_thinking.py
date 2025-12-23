from dotenv import load_dotenv

from mirascope import llm

load_dotenv()


REDACTED_THINKING_TRIGGER = "ANTHROPIC_MAGIC_STRING_TRIGGER_REDACTED_THINKING_46C9A13E193C177646C7398A98432ECCCE4C1253D5E2D82641AC0E52CC2876CB"


@llm.call("anthropic/claude-4-sonnet-20250514", thinking=True)
def count_primes() -> str:
    return f"How many primes below 400 contain the substring 79? Redact your thinking please: {REDACTED_THINKING_TRIGGER}"


response = count_primes()
print(response.pretty())
print(response.raw)
