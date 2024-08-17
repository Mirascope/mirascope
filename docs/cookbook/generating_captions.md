# Generate Captions for an Image

In this recipe, we go over how to use LLMs to generate a descriptive caption set of tags for an image with OpenAI’s `gpt-4o-mini`.

??? tip "Mirascope Concepts Used"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)
    - [Response Models](../learn/response_models.md)

!!! note "Background"

    Caption generation evolved from manual human effort to machine learning techniques like Conditional Random Fields (CRFs) and Support Vector Machines (SVMs), which were time-consuming and resource-intensive. Large Language Models (LLMs) have revolutionized this field, enabling efficient multi-modal tasks through API calls and prompt engineering, dramatically improving caption generation speed and accuracy.

!!! Warning

    This recipe will only work for those which support images (OpenAI, Gemini, Anthropic) as of 8/13/2024. Be sure to check if your provider has multimodal support.

With OpenAI’s multimodal capabilities, image inputs are treated just like text inputs, which means we can use it as context to ask questions or make requests. For the sake of reproducibility, we will get our image from a URL to save you the hassle of having to find and download an image. The image is [a public image from BBC Science of a wolf](https://c02.purpledshub.com/uploads/sites/41/2023/01/How-to-see-the-Wolf-Moon-in-2023--4bb6bb7.jpg?w=1880&webp=1) in front of the moon.

Since we can treat the image like any other text context, we can simply ask the model to caption the image:

```python
from mirascope.core import openai, prompt_template


url = "https://c02.purpledshub.com/uploads/sites/41/2023/01/How-to-see-the-Wolf-Moon-in-2023--4bb6bb7.jpg?w=940&webp=1"


@openai.call(model="gpt-4o-mini")
@prompt_template("Generate a short, descriptive caption for this image: {url:image}")
def generate_caption(url: str): ...


response = generate_caption(url)
print(response)
# > A majestic wolf howls in the night, silhouetted against the luminous full moon, creating a hauntingly beautiful scene that captures the spirit of the wild.
```

!!! tip "Additional Real-World Examples"
    - **Content Moderation**: Classify user-generated images as appropriate, inappropriate, or requiring manual review.
    - **Ecommerce Product Classification**: Create descriptions and features from product images.
    - **AI Assistant for People with Vision Impairments**: Convert images to text, then text-to-speech so people with vision impairments can be more independent.

When adapting this recipe to your specific use-case, consider the following:

- Refine your prompts to provide clear instructions and relevant context for your caption generation task.
- Experiment with different model providers and version to balance accuracy and speed.
- Use multiple model providers to evaluate results for accuracy.
- Use `async` for multiple images and run the calls in parallel.
