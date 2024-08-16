# JSON Mode

JSON Mode is a feature in Mirascope that allows you to request structured JSON output from Large Language Models (LLMs). This mode is particularly useful when you need to extract structured information from the model's responses, making it easier to parse and use the data in your applications.

## Support Across Providers

JSON Mode support varies across different LLM providers:

- **Explicit Support**: OpenAI, Gemini, Groq, Mistral
- **Pseudo Support**: Anthropic, Cohere

For providers with explicit support, Mirascope uses the native JSON Mode feature of the API. For providers without explicit support (Anthropic and Cohere), Mirascope implements a pseudo JSON Mode by instructing the model in the prompt to output JSON.

!!! note "Do It Yourself"

    If you'd prefer not to have any internal updates made to your prompt, you can always set JSON mode yourself through `call_params` rather than using the `json_mode` argument, which provides provider-agnostic support but is certainly not required to use JSON mode.

## Using JSON Mode

To enable JSON Mode, set `json_mode=True` when using the `call` decorator:

```python
import json
from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini", json_mode=True)
@prompt_template(
    """
    Provide the following information about {book_title}:
    - author
    - date published
    - genre
    """)
def get_book_info(book_title: str):
    ...


response = get_book_info("The Great Gatsby")
print(json.loads(response.content))
# > {"author": "F. Scott Fitzgerald", "date_published": "1925", "genre": "Tragedy"}
```

This will instruct the model to return its response in JSON format.

## Handling JSON Responses

When JSON Mode is enabled, the model's response will be a JSON string. You can parse this string using Python's built-in `json` module or other JSON parsing libraries (such as `jiter`):

```python
import json


response = get_book_info("The Great Gatsby")
book_info = json.loads(response.content)
print(book_info['author'])
```

## Error Handling and Validation

While JSON Mode significantly improves the structure of model outputs, it's important to note that it's not infallible. LLMs may occasionally produce invalid JSON or deviate from the expected structure. Therefore, it's crucial to implement proper error handling and validation in your code:

```python
import json

try:
    response = get_book_info("The Great Gatsby")
    json_obj = json.loads(response.content)
    print(json_obj["author"])
except json.JSONDecodeError:
    print("The model produced invalid JSON")
```

In the above example, we are only catching errors for invalid JSON. There is always still a chance that the LLM returns valid JSON that does not conform to your expected schema (such as field types). We recommend using [`Response Models`](./response_models.md) for easier structuring and validation of LLM outputs.

## Limitations and Considerations

- **Provider Differences**: The quality and consistency of JSON output may vary between providers, especially those using pseudo JSON Mode.
- **Performance**: Requesting structured JSON output may sometimes result in slightly longer response times compared to free-form text responses.

## Common Use Cases

JSON Mode is particularly useful in scenarios where you need to extract structured information from LLM responses, such as:

- Extracting specific details from text (e.g., names, dates, locations)
- Generating structured data for database entries
- Creating machine-readable summaries of documents
- Standardizing outputs for APIs or data pipelines

By leveraging JSON Mode, you can create more robust and data-driven applications that efficiently process and utilize LLM outputs.
