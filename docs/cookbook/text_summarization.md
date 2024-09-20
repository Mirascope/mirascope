# Text Summarization

In this recipe, we show some techniques to improve an LLM’s ability to summarize a long text from simple (e.g. `"Summarize this text: {text}..."`) to more complex prompting and chaining techniques. We will use OpenAI’s GPT-4o-mini model (128k input token limit), but you can use any model you’d like to implement these summarization techniques, as long as they have a large context window.

??? tip "Mirascope Concepts Used"

    - [Calls](../learn/calls.md)
    - [Chaining](../learn/chaining.md)
    - [Response Model](../learn/response_models.md)

!!! note "Background"

    Large Language Models (LLMs) have revolutionized text summarization by enabling more coherent and contextually aware abstractive summaries. Unlike earlier models that primarily extracted or rearranged existing sentences, LLMs can generate novel text that captures the essence of longer documents while maintaining readability and factual accuracy.

## Simple Call

For our examples, we’ll use the [Wikipedia article on python](https://en.wikipedia.org/wiki/Python_(programming_language)). We will be referring to this article as `wikipedia-python.txt`.

We will be using a simple call as our baseline:

```python
--8<-- "examples/cookbook/text_classification/text_summarization.py:3:51"
```

LLMs excel at summarizing shorter texts, but they often struggle with longer documents, failing to capture the overall structure while sometimes including minor, irrelevant details that detract from the summary's coherence and relevance.

One simple update we can make is to improve our prompt by providing an initial outline of the text then adhere to this outline to create its summary.

## Simple Call with Outline

This prompt engineering technique is an example of [Chain of Thought](https://www.promptingguide.ai/techniques/cot) (CoT), forcing the model to write out its thinking process. It also involves little work and can be done by modifying the text of the single call. With an outline, the summary is less likely to lose the general structure of the text.

```python
--8<-- "examples/cookbook/text_classification/text_summarization.py:53:186"
```

By providing an outline, we enable the LLM to better adhere to the original article's structure, resulting in a more coherent and representative summary.

For our next iteration, we'll explore segmenting the document by topic, requesting summaries for each section, and then composing a comprehensive summary using both the outline and these individual segment summaries.

## Segment then Summarize

This more comprehensive approach not only ensures that the model adheres to the original text's structure but also naturally produces a summary whose length is proportional to the source document, as we combine summaries from each subtopic.

To apply this technique, we create a `SegmentedSummary` Pydantic `BaseModel` to contain the outline and section summaries, and extract it in a chained call from the original summarize_text() call:

```python
--8<-- "examples/cookbook/text_classification/text_summarization.py:1:2"
--8<-- "examples/cookbook/text_classification/text_summarization.py:187:272"
```

!!! tip "Additional Real-World Applications"
    - **Meeting Notes**: Convert meeting from speech-to-text then summarize the text for reference.
    - **Education**: Create study guides or slides from textbook material using summaries.
    - **Productivity**: Summarize email chains, slack threads, word documents for your day-to-day.

When adapting this recipe to your specific use-case, consider the following:
    - Refine your prompts to provide clear instructions and relevant context for text summarization.
    - Experiment with different model providers and version to balance quality and speed.
    - Provide a feedback loop, use an LLM to evaluate the quality of the summary based on a criteria and feed that back into the prompt for refinement.

