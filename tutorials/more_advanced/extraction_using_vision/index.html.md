# Extraction using Vision

This recipe shows how to use LLMs — in this case, OpenAI GPT-4o and Anthropic Claude 3.5 Sonnet — to extract an image into a structured output using Mirascope’s `response_model`.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/response_models/">Response Models</a></li>
</ul>
</div>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p>
Traditionally, extracting text from images was done using Optical Character Recognition (OCR). LLMs have greatly enhanced the ability to automatically extract and analyze complex information from documents, significantly improving efficiency and accuracy in data processing tasks, since they have the ability to comprehend context, semantics, and implications within that text.
</p>
</div>

## Setup

To set up our environment, first let's install all of the packages we will use:


```python
!pip install "mirascope[openai]"
```


```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Extracting Receipt Items

We define an `Item` model that has some information we care to extract.


```python
from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str = Field(..., description="The name of the item")
    quantity: int = Field(..., description="The quantity of the item")
    price: float = Field(..., description="The price of the item")
```

## Creating the prompt

There are differences between how providers handle their multimodal inputs. For example, OpenAI supports passing in images directly, whereas Anthropic requires the image to be base64 encoded. Mirascope eliminates the need to handle these providers differently and unifies the interface for you. For all providers that support multimodal, we can take advantage of Mirascope parsing and pass in the image directly via `{<variable_name>:image}`.
Also, We set the `response_model` to `list[Item]` so that our LLM knows to extract each item.



```python
from mirascope.core import anthropic, openai, prompt_template


@openai.call(model="gpt-4o", response_model=list[Item])
@prompt_template(
    """
    SYSTEM:
    Extract the receipt information from the image.
    
    USER:
    {url:image}
    """
)
def extract_receipt_info_openai(url: str): ...


@anthropic.call(
    model="claude-3-5-sonnet-20240620", response_model=list[Item], json_mode=True
)
@prompt_template(
    """
    Extract the receipt information from the image.
    
    {url:image}
    """
)
def extract_receipt_info_anthropic(url: str): ...
```

let's get the results:


```python
import base64

import httpx

image_url = "https://www.receiptfont.com/wp-content/uploads/template-mcdonalds-1-screenshot-fit.png"

image_media_type = "image/png"
image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")

print(extract_receipt_info_openai(image_url))

print(extract_receipt_info_anthropic(image_url))
```

    [Item(name='Happy Meal 6 Pc', quantity=1, price=4.89), Item(name='Snack Oreo McFlurry', quantity=1, price=2.69)]
    [Item(name='Happy Meal 6 Pc', quantity=1, price=4.89), Item(name='Snack Oreo McFlurry', quantity=1, price=2.69)]


We see that both LLMs return the same response which gives us more confidence that the image was extracted accurately, but it is not guaranteed.

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Examples</p>
<ul>
<li><b>Split your Bill</b>: Building off our example, we can upload our receipt along with a query stating who ordered what dish and have the LLM split the bill for you.</li>
<li><b>Content Moderation</b>: Classify user-generated images as appropriate, inappropriate, or requiring manual review.</li>
<li><b>Ecommerce Product Classification</b>: Create descriptions and features from product images.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider the following:

- Refine your prompts to provide clear instructions and relevant context for your image extraction. In our example, there were sub-items that were not extracted, which depending on your situation may need to be extracted as well.
- Experiment with different model providers and version to balance accuracy and speed.
- Use multiple model providers to verify if results are correct.
- Use `async` for multiple images and run the calls in parallel.

