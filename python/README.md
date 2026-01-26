# Mirascope Python

This directory contains the Python implementation of Mirascope: The LLM Anti-Framework. It's intended as a "Goldilocks API" that affords the fine-grained control you'd get from using raw provider APIs, as well as the type safety and easy ergonomics that are offered by higher-level agent frameworks. Think of Mirascope as the "React" of LLM development, where provider native APIs are HTML/CSS, and the agent frameworks are Angular.

## Documentation 

- [Why use Mirascope?](https://mirascope.com/docs/why)
- [Mirascope Quickstart](https://mirascope.com/docs/quickstart)
- [Mirascope Concepts](https://mirascope.com/docs/learn/llm)

## Installation

```bash
# using uv, with all provider deps
uv add "mirascope[all]"

# using uv, with just Anthropic
uv add "mirascope[anthropic]"

# using pip, with all deps 
pip install "mirascope[all]"

# using pip, just OpenAI
pip install "mirascope[openai]"
```

## Usage

Here's an example of creating a simple agent, with tool-calling and streaming, using Mirascope. For many more examples, [read the docs](https://mirascope.com/docs).

```python
from mirascope import llm

@llm.tool
def exp(a: float, b: float) -> float:
   """Compute an exponent"""
   return a ** b

@llm.tool
def add(a: float, b: float) -> float:
   """Add two numbers"""
   return a + b

model = llm.Model("anthropic/claude-haiku-4-5")
response = model.stream("What is 42 ** 4 + 37 ** 3?", tools=[exp, add])

while True:
   for stream in response.streams():
         if stream.content_type == "text":
            for delta in stream:
               print(delta, end="", flush=True)
         elif stream.content_type == "tool_call":
            stream.collect()  # consume the stream
            print(f"\n> Calling {stream.tool_name}({stream.partial_args})")
   print()
   if response.tool_calls:
         response = response.resume(response.execute_tools())
   else:
         break
```

## Development Setup

1. **Environment Variables**: Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   # Necessary for updating e2e snapshot tests
   ```

2. **Install Dependencies**:

   ```bash
   cd python
   uv sync --all-extras --dev
   ```

## Helpful Commands:

Here are helpful development commands. All must be run from within the `python` directory.

- `uv run pyright .`

Run typechecking.

- `uv run ruff check --fix .`

Check ruff linter (fixing issues where possible).

- `uv run ruff format .`

Run ruff formatter.

- `uv run pytest`

Run all Python unit tests.

- `uv run pytest --cov --cov-config=.coverargc --cov-report=term-missing`

Run all Python unit tests, and report code coverage. (We require 100% coverage in CI.)

- `uv run pytest --fix`

Run all Python unit tests, and update any changed snapshots.

- `uvx codespell --config ../.codespellrc`

Run codespell, identifying many common spelling mistakes.

## Typechecking

We prize type safety, both on the API surface and internally. You can run typechecking via `uv run pyright .` within this `python/` directory. (We're looking into supporting `ty` so as to speed up our typechecking.)

## Testing

This project makes extensive use of e2e tests, which replay real interactions with various LLM providers to ensure that Mirascope truly works on the providers' APIs. We use [VCR.py](https://vcrpy.readthedocs.io/) and [inline-snapshot](https://15r10nk.github.io/inline-snapshot/) to maintain these e2e tests. For more details, read [tests/e2e/README.md](./tests/e2e/README.md).

If you make changes to Mirascope that require new snapshots, you should manually delete the outdated cassette files, and then run `uv run pytest python/tests/e2e --fix`. Note that doing so requires real API keys in your `.env` file.

We require 100% code coverage in CI. You can get a code coverage report via:

`uv run pytest --cov --cov-config=.coverargc --cov-report=term-missing`

## Read More

For more info on contributing, read [the contributing page in our docs](https://mirascope.com/docs/contributing).
