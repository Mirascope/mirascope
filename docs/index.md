# Getting Started with Mirascope

Mirascope: Build powerful LLM applications with ease.

## Quick Start

Install Mirascope and set up your API key:

```bash
pip install "mirascope[openai]"  # For OpenAI support
pip install "mirascope[anthropic]"  # For Anthropic support
# For other providers, use: pip install "mirascope[provider_name]"
```

```python
import os
os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# For Anthropic: os.environ["ANTHROPIC_API_KEY"] = "YOUR_API_KEY"
```
Mirascope supports various LLM providers, including [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), [Mistral](https://mistral.ai/), [Gemini](https://gemini.google.com), [Groq](https://groq.com/), [Cohere](https://cohere.com/), [LiteLLM](https://www.litellm.ai/), [Azure AI](https://azure.microsoft.com/en-us/solutions/ai), and [Vertex AI](https://cloud.google.com/vertex-ai).


Create your first LLM-powered function:

```python
from mirascope.core import openai, prompt_template

@openai.call("gpt-4o-mini")
@prompt_template("What is the capital of {country}?")
def get_capital(country: str): ...

response = get_capital("Japan")
print(response.content)
# Output: The capital of Japan is Tokyo.
```

Example of streaming responses:

```python
@openai.call("gpt-4o-mini", stream=True)
@prompt_template("Write a short story about {topic}")
def stream_story(topic: str): ...

for chunk, _ in stream_story("a magical forest"):
    print(chunk.content, end="", flush=True)
```

## Choose Your Path

### For Newcomers
1. Explore our Jupyter notebooks:
   - [Quickstart Guide](https://github.com/Mirascope/mirascope/blob/dev/examples/getting_started/quickstart.ipynb): Comprehensive overview of core features
   - [Dynamic Configuration and Chaining](https://github.com/Mirascope/mirascope/blob/dev/examples/getting_started/dynamic_configuration_and_chaining.ipynb): Various examples ranging from basic usage to more complex chaining techniques
   - [Tools and Agents](https://github.com/Mirascope/mirascope/blob/dev/examples/getting_started/tools_and_agents.ipynb): Learn to build advanced AI agents
   - [Evaluation Techniques](https://github.com/Mirascope/mirascope/blob/dev/examples/getting_started/evaluation.ipynb): Assess and improve LLM outputs
2. Explore our [Cookbook](./cookbook/index.md): Advanced patterns and real-world applications

### For Experienced Developers
1. Check out our [Learn Documentation](./learn/index.md): In-depth exploration of Mirascope capabilities
2. Refer to the [API Reference](./api/index.md): Detailed information on classes and functions
3. Explore our [Cookbook](./cookbook/index.md): Advanced patterns and real-world applications

## Key Features

- LLM Calls: Simplified API interactions across multiple providers
- Prompt Templates: Dynamic prompt creation with type-safe templating
- Custom Tools: Extend LLM capabilities with your own functions
- Streaming: Real-time responses for improved user experience
- Agent State Management: Maintain conversation context and history effortlessly

## Next Steps

- Read [Why Use Mirascope?](WHY.md) to understand our unique advantages
- Join our [Slack Community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA) for support and collaboration
- Star us on [GitHub](https://github.com/Mirascope/mirascope) to stay updated with the latest developments

Ready to revolutionize your LLM development? Let's get started with Mirascope!