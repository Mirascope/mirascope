# Extraction using Vision

This recipe shows how to use LLMs — in this case, OpenAI GPT-4o and Anthropic Claude 3.5 Sonnet — to extract an image into a structured output using Mirascope’s `response_model`.

??? tip "Mirascope Concepts Used"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)
    - [Response Models](../learn/response_models.md)

!!! note "Background"

    Traditionally, extracting text from images was done using Optical Character Recognition (OCR). LLMs have greatly enhanced the ability to automatically extract and analyze complex information from documents, significantly improving efficiency and accuracy in data processing tasks, since they have the ability to comprehend context, semantics, and implications within that text.

## Creating the prompt

There are differences between how providers handle their multimodal inputs. For example, OpenAI supports passing in images directly, whereas Anthropic requires the image to be base64 encoded. Mirascope eliminates the need to handle these providers differently and unifies the interface for you. For all providers that support multimodal, we can take advantage of Mirascope parsing and pass in the image directly via `{<variable_name>:image}`.
```python
--8<-- "examples/cookbook/extraction_using_vision.py:1:3"
--8<-- "examples/cookbook/extraction_using_vision.py:5:7"
--8<-- "examples/cookbook/extraction_using_vision.py:20:43"
```

Now that both models can read the image properly, it is time to add our structured output using `response_model` .

## Extracting Receipt Items

We define an `Item` model that has some information we care to extract. We set the `response_model` to `list[Item]` so that our LLM knows to extract each item, like so:

```python
--8<-- "examples/cookbook/extraction_using_vision.py:4:5"
--8<-- "examples/cookbook/extraction_using_vision.py:14:17"
```

Now that we have defined our `response_model`, let's get the results:

```python
--8<-- "examples/cookbook/extraction_using_vision.py:46:51"
--8<-- "examples/cookbook/extraction_using_vision.py:52:61"
```

We see that both LLMs return the same response which gives us more confidence that the image was extracted accurately, but it is not guaranteed.

!!! tip "Additional Real-World Examples"

    - **Split your Bill**: Building off our example, we can upload our receipt along with a query stating who ordered what dish and have the LLM split the bill for you.
    - **Content Moderation**: Classify user-generated images as appropriate, inappropriate, or requiring manual review.
    - **Ecommerce Product Classification**: Create descriptions and features from product images.

When adapting this recipe to your specific use-case, consider the following:

- Refine your prompts to provide clear instructions and relevant context for your image extraction. In our example, there were sub-items that were not extracted, which depending on your situation may need to be extracted as well.
- Experiment with different model providers and version to balance accuracy and speed.
- Use multiple model providers to verify if results are correct.
- Use `async` for multiple images and run the calls in parallel.
