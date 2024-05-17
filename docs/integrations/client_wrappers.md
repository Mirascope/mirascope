# Client Wrappers

If you want to use Mirascope in conjunction with another library which implements a client wrapper (such as LangSmith), you can do so easily by setting the `wrapper` parameter within your call parameters. For example, setting this call parameter on an `OpenAICall` will internally wrap the `OpenAI` client within an `OpenAICall`, giving you access to both sets of functionalities. This will work for any of the providers we support.

```python
from some_library import some_wrapper
from mirascope.openai import OpenAICall
from mirascope.base import BaseConfig

class BookRecommender(OpenAICall):
    prompt_template = "Can you recommend some books on {topic}?"

    topic: str

    configuration = BaseConfig(client_wrappers=[some_wrapper])
```

Now, every call to `call`, `call_async`, `stream`, and `stream_async` will be executed on top of the wrapped `OpenAI` client.
