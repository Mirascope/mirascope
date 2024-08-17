# HyperDX

Mirascope provides out-of-the-box integration with [HyperDX](https://www.hyperdx.io/).

You can install the necessary packages directly or using the `hyperdx` extras flag:

```python
pip install "mirascope[hyperdx]"
```

## How to use HyperDX with Mirascope

### Calls

Our integration with HyperDX is a simple wrapper on top of our OpenTelemetry integration. The `with_hyperdx` decorator can be used on all Mirascope functions to automatically log calls across all [supported LLM providers](../learn/calls.md#supported-providers).

Here is a simple example using tools:

```python
import os

from mirascope.core import anthropic, prompt_template
from mirascope.integrations.otel import with_hyperdx

os.environ["HYPERDX_API_KEY"] = "YOUR_API_KEY"


def format_book(title: str, author: str):
    return f"{title} by {author}"


@with_hyperdx()
@anthropic.call(model="claude-3-5-sonnet-20240620", tools=[format_book])
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str):
    ...


print(recommend_book("fantasy"))
```

Refer to the [OpenTelemetry documentation](./otel.md) for more details.
