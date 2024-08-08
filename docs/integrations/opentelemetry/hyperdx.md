# HyperDX

Mirascope provides out-of-the-box integration with [HyperDX](https://www.hyperdx.io/).

## How to use HyperDX with Mirascope

Get an API key from HyperDX and set your environment variable

```bash
# .env
HYPERDX_API_KEY="..."
```

```python
from mirascope.integrations.otel import with_hyperdx
```

## Examples

### Call

A Mirascope call with tools:

```python
from mirascope.core import anthropic, prompt_template
from mirascope.integrations.otel import with_hyperdx

def format_book(title: str, author: str):
    return f"{title} by {author}"

@with_hyperdx
@anthropic.call(model="claude-3-5-sonnet-20240620", tools=[format_book])
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...

print(recommend_book("fantasy"))
```

Refer to the [OpenTelemetry documentation](ADD LINK) for more details.
