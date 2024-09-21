# Removing Semantic Duplicates

 In this recipe, we show how to use LLMs — in this case, OpenAI's `gpt-4o-mini` — to answer remove semantic duplicates from lists and objects.

??? tip "Mirascope Concepts Used"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)
    - [Response Model](../learn/response_models.md)

!!! note "Background"

    Semantic deduplication, or the removal of duplicates which are equivalent in meaning but not in data, has been a longstanding problem in NLP. LLMs which have the ability to comprehend context, semantics, and implications within that text trivializes this problem.


## Deduplicating a List

To start, assume we have a some entries of movie genres with semantic duplicates:

```python
--8<-- "examples/cookbook/removing_semantic_duplicates.py:15:26"
```

To deduplicate this list, we’ll extract a schema containing `genres`, the deduplicated list, and `duplicates`, a list of all duplicate items. The reason for having `duplicates` in our schema is that LLM extractions can be inconsistent, even with the most recent models - forcing it to list the duplicate items helps it reason through the call and produce a more accurate answer.

```python
--8<-- "examples/cookbook/removing_semantic_duplicates.py:1:2"
--8<-- "examples/cookbook/removing_semantic_duplicates.py:5:12"
```

We can now set this schema as our response model in a Mirascope call:

```python
--8<-- "examples/cookbook/removing_semantic_duplicates.py:3:5"
--8<-- "examples/cookbook/removing_semantic_duplicates.py:29:52"
```

## Deduplicating Objects

Since Mirascope’s prompt templates can parse anything that can have `str()` called on it, we can parse more complex objects as well, with greater and more types of differences between semantically equivalent objects. Here we define a `Book` Pydantic Model and provide a list books with multiple entries, where entries differ in data via typos, title formatting, spacing, and genre classification:

```python
--8<-- "examples/cookbook/removing_semantic_duplicates.py:56:73"
```

Just like with a list of strings, we can create a schema of `DeduplicatedBooks` and set it as the response model, with a modified prompt to account for the different types of differences we see:

```python
--8<-- "examples/cookbook/removing_semantic_duplicates.py:76:102"
```

!!! tip "Additional Real-World Examples"

    - **Customer Relationship Management (CRM)**: Maintaining a single, accurate view of each customer.
    - **Database Management**: Removing duplicate records to maintain data integrity and improve query performance
    - **Email**: Clean up digital assets by removing duplicate attachments, emails.

When adapting this recipe to your specific use-case, consider the following:

- Refine your prompts to provide clear instructions and examples tailored to your requirements.
- Experiment with different model providers and version to balance accuracy and speed.
- Use multiple model providers to evaluate whether all duplicates have bene removed.
- Add more information if possible to get better accuracy, e.g. some books might have similar names but are released in different years.
