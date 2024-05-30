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

We currently do not have out-of-the-box cost tracking for streaming yet, but this is something we are working on. In the meantime, you can use this `OpenAICall.stream` example:

```python
import os

from mirascope.openai import OpenAICall
from mirascope.openai.utils import openai_api_calculate_cost

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

class BookRecommender(OpenAICall):
    prompt_template = "Please recommend a {genre} book."

    genre: str


stream = BookRecommender(genre="fantasy").stream()
for chunk in stream:
    print(chunk.content, end="")
    if chunk.cost:
        print(chunk.cost)
# > 0.00013099999999999999
```
!!! note

    Many providers do not support usage statistics for streaming yet. Once a provider adds usage for streaming, we will add cost for streaming.
    
## How come I am receiving None back when trying to access cost

!!! note

    GeminiCall `.cost` will always return None because the `google.generativeai` package does not give back usage statistics.

For other providers, this typically means that the response did not contain Usage statistics or more commonly, you're using a brand new model that we haven't added to our cost calculation function. If you happen to use a model that we have not added yet, feel free to send a pull request to update our cost function (Let's say for [OpenAI](https://github.com/Mirascope/mirascope/blob/dev/mirascope/openai/utils.py)) or ping us in the [Mirascope Slack](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA).
