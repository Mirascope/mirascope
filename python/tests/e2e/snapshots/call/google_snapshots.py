from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
To find the sum of 4200 + 42, you can add them:

   4200
+    42
-------
   4242

So, 4200 + 42 = **4242**.\
"""
                    )
                ]
            ),
        ],
        "format_type": None,
    }
)
async_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
To find the sum of 4200 + 42, we can add the numbers:

   4200
+    42
-------
   4242

So, 4200 + 42 = **4242**.\
"""
                    )
                ]
            ),
        ],
        "format_type": None,
    }
)
stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
To find the sum of 4200 and 42, we can add them:

```
  4200
+   42
------
  4242
```

So, 4200 + 42 = **4242**.\
"""
                    )
                ]
            ),
        ],
        "format_type": None,
        "n_chunks": 4,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
To find the sum of 4200 + 42, you can add the numbers:

   4200
+    42
-------
   4242

So, 4200 + 42 = **4242**.\
"""
                    )
                ]
            ),
        ],
        "format_type": None,
        "n_chunks": 4,
    }
)
