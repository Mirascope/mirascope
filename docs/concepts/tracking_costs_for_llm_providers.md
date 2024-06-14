# Tracking Costs for LLM Providers

One developer experience that we found frustrating at Mirascope is how LLM providers only return usage statistics and not cost, so we built it into our `BaseCallResponse`. For every provider you can access the `.cost` property or use the `.dump()` function.

## Simple Example

```python
import os

from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class BookRecommender(OpenAICall):
    prompt_template = "Please recommend a {genre} book."

    genre: str


response = BookRecommender(genre="fantasy").call()
print(response.cost)
# > 0.00011449999999999999
```

## Cost tracking for streaming

Mirascope implements a [`BaseStream`](https://docs.mirascope.io/latest/api/base/types/#mirascope.base.types.BaseStream) class which adds convenience to streaming. Each provider has their own respective class, e.g. if you are using OpenAI, you will use `OpenAIStream`.
Wrap the stream with `OpenAIStream` to gain access to metadata such as cost for streaming:

```python
import os

from mirascope.openai import OpenAICall, OpenAIStream

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

class BookRecommender(OpenAICall):
    prompt_template = "Please recommend a {genre} book."

    genre: str


stream = BookRecommender(genre="fantasy").stream()
openai_stream = OpenAIStream(stream)
for chunk, tool in openai_stream:
    print(chunk.content, end="")
print(openai_stream.cost)
# > 0.00013099999999999999
```

!!! note

    Many providers do not support usage statistics for streaming yet. Once a provider adds usage for streaming, we will add cost for streaming.
    
## How come I am receiving `None` back when trying to access cost

!!! note

    GeminiCall `.cost` will always return None because the `google.generativeai` package does not give back usage statistics.

For other providers, this typically means that the response did not contain Usage statistics or more commonly, you're using a brand new model that we haven't added to our cost calculation function. If you happen to use a model that we have not added yet, feel free to send a pull request to update our cost function (e.g. [OpenAI](https://github.com/Mirascope/mirascope/blob/dev/mirascope/openai/utils.py)) or ping us in the [Mirascope Slack](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA).
