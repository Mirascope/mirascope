from anthropic import RateLimitError as AnthropicRateLimitError
from mirascope import llm, prompt_template
from mirascope.retries import FallbackError, fallback
from openai import RateLimitError as OpenAIRateLimitError


@fallback(
    OpenAIRateLimitError,
    [
        {
            "catch": AnthropicRateLimitError,
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-latest",
        }
    ],
)
@llm.call("openai", "gpt-4o-mini")
@prompt_template("Answer this question: {question}")
def answer_question(question: str): ...


try:
    response = answer_question("What is the meaning of life?")
    if caught := getattr(response, "_caught", None):
        print(f"Exception caught: {caught}")
    print("### Response ###")
    print(response.content)
except FallbackError as e:
    print(e)
