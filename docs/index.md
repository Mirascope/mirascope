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
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str):
    ...

print(recommend_book("fantasy"))
# > I recommend "The Name of the Wind" by Patrick Rothfuss.
```

Easily generate a structured output instead:

```python
from mirascope.core import openai, prompt_template
from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str

@openai.call("gpt-4o-mini", response_model=Book)
@prompt_template("Extract {book}")
def extract_book(book: str): ...

book = extract_book("The Name of the Wind by Patrick Rothfuss")
assert isinstance(book, Book)
print(book)
# > title='The Name of the Wind' author='Patrick Rothfuss'
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

- Prompt Templates: Dynamic prompt creation with type-safe templating
- LLM Calls: Simplified API interactions across multiple providers
- Streaming: Real-time responses for improved user experience
- Custom Tools: Extend LLM capabilities with your own functions
- Agent: Effortless manage state and integrate custom tools

## Next Steps

- Read [Why Use Mirascope?](WHY.md) to understand our unique advantages
- Join our [Slack Community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA) for support and collaboration
- Star us on [GitHub](https://github.com/Mirascope/mirascope) to stay updated with the latest developments

We're excited to see what you'll build with Mirascope, and we're here to help! Don't hesitate to reach out :)