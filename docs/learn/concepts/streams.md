# Streams

This section only covers features unique to streaming, as opposed to general Mirascope calls. To see more details about calling a model, check out the Calls section[link].

To stream a Mirascope call, set the flag `stream=True` in the  `call` decorator, regardless of whether the provider’s API uses a separate function or a different flag. 

```python
from mirascope.core import openai

@openai.call(model="gpt-4o", stream=True)
def recommend_book(genre: str):
    """Recommend a {genre} book."""
    
stream = recommend_book(genre="fantasy")

for chunk, _ in stream:
	print(chunk.content, end="", flush=True)
# > Certainly! If you're looking for a compelling fantasy book, ...
```

## Stream Responses

Streaming with Mirascope returns a provider-specific subclass of `BaseStream`, which generates the provider-specific subclass of `BaseCallResponseChunk`. In the snippet above, it’s an `OpenAIStream[OpenAIResponseChunk]`

Like standard calls, these wrapper classes allows you to easily access important properties relevant to your stream. However, there are some key differences outlined below.

### Stream vs. Chunks

Not every chunk in a streams contains meaningful metadata, so we collect useful information in the stream object. You can access fields like `usage`, `cost`, `message_param`, and `user_message_param` once the stream is exhausted.

```python
@openai.call(model="gpt-4o", stream=True)
def recommend_book(genre: str):
    """Recommend a {genre} book."""
    
results = recommend_book(genre="fantasy")

# iterate through stream first
for chunk, _ in results:
	# do stuff with `chunk` 
	
# now available
print(results.usage)
# > CompletionUsage(completion_tokens=102, prompt_tokens=12, total_tokens=114)

print(results.cost)
# > 0.00042

print(results.message_param)
# > {'content': 'Certainly! ..., 'role': `assistant`}

print(results.user_message_param)
# > {'content': 'Recommend a fantasy book.', 'role': 'user'} 
```

### Chunk From Provider API

We still provide the original object from the provider’s API, but now access it through the `chunk` property instead.

```python
for chunk, _ in results:
    print(chunk.chunk)
    
# > ChatCompletionChunk(...)
#   ChatCompletionChunk(...)
#   ChatCompletionChunk(...)
#   ...
```

To see the full list of convenience wrappers, check out the API reference for _stream.py[link] and _call_response_chunk.py[link]

## Async

If you want concurrency, use `call_async` to make an asynchronous call with `stream=True`.

```python
import asyncio
from mirascope.core import openai

@openai.call_async(model="gpt-4o", stream=True)
async def recommend_book(genre: str):
    """Recommend a {genre} book."""
    
async def run():
    results = await recommend_book(genre="fiction")
    async for chunk, _ in results:
        print(chunk.content, end="", flush=True)
        
asyncio.run(run())
# > Certainly! If you're looking for a compelling fantasy book, ...
```
