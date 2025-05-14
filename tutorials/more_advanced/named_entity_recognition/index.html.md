# Named Entity Recognition

This guide demonstrates techniques to perform Named Entity Recognition (NER) using Large Language Models (LLMs) with various levels of nested entity recognition. We'll use Groq's llama-3.1-8b-instant model, but you can adapt this approach to other models with similar capabilities.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/response_models/">Response Model</a></li>
</ul>
</div>

<div class="admonition info">
<p class="admonition-title">Background</p>
<p>
Named Entity Recognition is a subtask of information extraction that seeks to locate and classify named entities in text into predefined categories such as person names, organizations, locations, etc. LLMs have revolutionized NER by enabling more context-aware and hierarchical entity recognition, going beyond traditional rule-based or statistical methods.
</p>
</div>

<div class="admonition warning">
<p class="admonition-title">LLMs are not trained specifically for NER</p>
<p>
It's worth noting that there are models that are trained specifically for NER (such as GLiNER). These models are often much smaller and cheapr and can often get better results for the right tasks. LLMs should generally be reserved for quick and dirty prototyping for NER or for tasks that may require a more nuanced, open-ended language-based approach. For example, an NER system that accepts user input to guide the system by be easier to build using LLMs than a traditionally trained NER-specific model.
</p>
</div>

## Setup

To set up our environment, first let's install all of the packages we will use:


```python
!pip install "mirascope[groq]" pytest
!pip install ipytest # For running pytest in Jupyter Notebooks
```


```python
import os

os.environ["GROQ_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Simple NER

We'll implement NER with different levels of complexity: simple and nested entity recognition. Let's start with the simple version:



```python
from __future__ import annotations  # noqa: F404

import textwrap

from mirascope.core import groq, prompt_template
from pydantic import BaseModel, Field

unstructured_text = """
Apple Inc., the tech giant founded by Steve Jobs and Steve Wozniak, recently announced a partnership with OpenAI, the artificial intelligence research laboratory consisting of the for-profit corporation OpenAI LP and its parent company, the non-profit OpenAI Inc. This collaboration aims to enhance Siri, Apple's virtual assistant, which competes with Amazon's Alexa and Google Assistant, a product of Alphabet Inc.'s Google division. The joint project will be led by Apple's AI chief John Giannandrea, a former Google executive, and will take place at Apple Park, the company's headquarters in Cupertino, California.
"""


class SimpleEntity(BaseModel):
    entity: str = Field(description="The entity found in the text")
    label: str = Field(
        description="The label of the entity (e.g., PERSON, ORGANIZATION, LOCATION)"
    )


@groq.call(
    model="llama-3.1-8b-instant",
    response_model=list[SimpleEntity],
    json_mode=True,
    call_params={"temperature": 0.0},
)
def simple_ner(text: str) -> str:
    return f"Extract the entities from this text: {text}"


print("Simple NER Results:")
simple_result = simple_ner(unstructured_text)
for entity in simple_result:
    print(f"Entity: {entity.entity}, Label: {entity.label}")
```

    Simple NER Results:
    Entity: Apple Inc., Label: ORGANIZATION
    Entity: Steve Jobs, Label: PERSON
    Entity: Steve Wozniak, Label: PERSON
    Entity: OpenAI, Label: ORGANIZATION
    Entity: OpenAI LP, Label: ORGANIZATION
    Entity: OpenAI Inc., Label: ORGANIZATION
    Entity: Amazon, Label: ORGANIZATION
    Entity: Google, Label: ORGANIZATION
    Entity: Alphabet Inc., Label: ORGANIZATION
    Entity: John Giannandrea, Label: PERSON
    Entity: Apple Park, Label: LOCATION
    Entity: Cupertino, Label: LOCATION
    Entity: California, Label: LOCATION



In this example, we're extracting entities that have just the entity's text and label. However, entities often have relationships that are worth extracting and understanding.

## Nested NER

Now, let's implement a more sophisticated version that can handle nested entities:



```python
class NestedEntity(BaseModel):
    entity: str = Field(description="The entity found in the text")
    label: str = Field(
        description="The label of the entity (e.g., PERSON, ORGANIZATION, LOCATION)"
    )
    parent: str | None = Field(
        description="The parent entity if this entity is nested within another entity",
        default=None,
    )
    children: list[NestedEntity] = Field(
        default_factory=list, description="Nested entities within this entity"
    )


@groq.call(
    model="llama-3.1-8b-instant",
    response_model=list[NestedEntity],
    json_mode=True,
    call_params={"temperature": 0.0},
)
@prompt_template(
    """
    Identify all named entities in the following text, including deeply nested entities. 
    For each entity, provide its label and any nested entities within it.

    Guidelines:
    1. Identify entities of types PERSON, ORGANIZATION, LOCATION, and any other relevant types.
    2. Capture hierarchical relationships between entities.
    3. Include all relevant information, even if it requires deep nesting.
    4. Be thorough and consider all possible entities and their relationships.

    Example:
    Text: "John Smith, the CEO of Tech Innovations Inc., a subsidiary of Global Corp, announced a new product at their headquarters in Silicon Valley."
    Entities:
    - Entity: "John Smith", Label: "PERSON", Parent: None
      Children:
        - Entity: "Tech Innovations Inc.", Label: "ORGANIZATION", Parent: "John Smith"
          Children:
            - Entity: "Global Corp", Label: "ORGANIZATION", Parent: "Tech Innovations Inc."
    - Entity: "Silicon Valley", Label: "LOCATION", Parent: None

    Now, analyze the following text: {text}
    """
)
def nested_ner(text: str): ...


print("\nNested NER Results:")
improved_result = nested_ner(unstructured_text)


def print_nested_entities(entities, level=0):
    for entity in entities:
        indent = "  " * level
        entity_info = (
            f"Entity: {entity.entity}, Label: {entity.label}, Parent: {entity.parent}"
        )
        print(textwrap.indent(entity_info, indent))
        if entity.children:
            print_nested_entities(entity.children, level + 1)


print_nested_entities(improved_result)
```

    
    Nested NER Results:
    Entity: Steve Jobs, Label: PERSON, Parent: None
      Entity: Apple Inc., Label: ORGANIZATION, Parent: Steve Jobs
        Entity: Steve Wozniak, Label: PERSON, Parent: Apple Inc.
        Entity: Apple Park, Label: LOCATION, Parent: Apple Inc.
        Entity: Cupertino, Label: LOCATION, Parent: Apple Park
        Entity: California, Label: LOCATION, Parent: Cupertino
    Entity: Steve Wozniak, Label: PERSON, Parent: None
      Entity: Apple Inc., Label: ORGANIZATION, Parent: Steve Wozniak
    Entity: Apple Inc., Label: ORGANIZATION, Parent: None
      Entity: John Giannandrea, Label: PERSON, Parent: Apple Inc.
      Entity: Apple Park, Label: LOCATION, Parent: Apple Inc.
      Entity: Cupertino, Label: LOCATION, Parent: Apple Park
      Entity: California, Label: LOCATION, Parent: Cupertino
      Entity: OpenAI, Label: ORGANIZATION, Parent: Apple Inc.
        Entity: OpenAI LP, Label: ORGANIZATION, Parent: OpenAI
        Entity: OpenAI Inc., Label: ORGANIZATION, Parent: OpenAI
    Entity: John Giannandrea, Label: PERSON, Parent: None
      Entity: Apple Inc., Label: ORGANIZATION, Parent: John Giannandrea
    Entity: Apple Park, Label: LOCATION, Parent: None
      Entity: Cupertino, Label: LOCATION, Parent: Apple Park
      Entity: California, Label: LOCATION, Parent: Cupertino
    Entity: Cupertino, Label: LOCATION, Parent: None
      Entity: California, Label: LOCATION, Parent: Cupertino
    Entity: California, Label: LOCATION, Parent: None
    Entity: OpenAI, Label: ORGANIZATION, Parent: None
      Entity: OpenAI LP, Label: ORGANIZATION, Parent: OpenAI
      Entity: OpenAI Inc., Label: ORGANIZATION, Parent: OpenAI
    Entity: OpenAI LP, Label: ORGANIZATION, Parent: None
    Entity: OpenAI Inc., Label: ORGANIZATION, Parent: None
    Entity: Amazon, Label: ORGANIZATION, Parent: None
      Entity: Alexa, Label: PRODUCT, Parent: Amazon
    Entity: Alexa, Label: PRODUCT, Parent: None
    Entity: Google, Label: ORGANIZATION, Parent: None
      Entity: Google Assistant, Label: PRODUCT, Parent: Google
      Entity: Alphabet Inc., Label: ORGANIZATION, Parent: Google
    Entity: Google Assistant, Label: PRODUCT, Parent: None
    Entity: Alphabet Inc., Label: ORGANIZATION, Parent: None



## Testing

To ensure robustness, it's crucial to test the NER system with diverse scenarios. Here's a function to run multiple test cases:



```python
import ipytest  # noqa: E402
import pytest  # noqa: E402

ipytest.autoconfig()


test_cases = [
    (
        """
    The multinational conglomerate Alphabet Inc., parent company of Google, has acquired 
    DeepMind, a leading AI research laboratory based in London. DeepMind's founder, 
    Demis Hassabis, will join Google Brain, a division of Google AI, as Chief AI Scientist. 
    This move strengthens Alphabet's position in the AI field, challenging competitors like 
    OpenAI, which is backed by Microsoft, and Facebook AI Research, a part of Meta Platforms Inc.
        """,
        [
            NestedEntity(
                entity="Alphabet Inc.",
                label="ORGANIZATION",
                parent=None,
                children=[
                    NestedEntity(
                        entity="Google",
                        label="ORGANIZATION",
                        parent="Alphabet Inc.",
                        children=[
                            NestedEntity(
                                entity="Google Brain",
                                label="ORGANIZATION",
                                parent="Google",
                                children=[],
                            ),
                            NestedEntity(
                                entity="Google AI",
                                label="ORGANIZATION",
                                parent="Google",
                                children=[
                                    NestedEntity(
                                        entity="Google Brain",
                                        label="ORGANIZATION",
                                        parent="Google AI",
                                        children=[],
                                    )
                                ],
                            ),
                        ],
                    ),
                    NestedEntity(
                        entity="DeepMind",
                        label="ORGANIZATION",
                        parent="Alphabet Inc.",
                        children=[
                            NestedEntity(
                                entity="Demis Hassabis",
                                label="PERSON",
                                parent="DeepMind",
                                children=[],
                            )
                        ],
                    ),
                ],
            ),
            NestedEntity(entity="London", label="LOCATION", parent=None, children=[]),
            NestedEntity(
                entity="Demis Hassabis", label="PERSON", parent=None, children=[]
            ),
            NestedEntity(
                entity="OpenAI",
                label="ORGANIZATION",
                parent=None,
                children=[
                    NestedEntity(
                        entity="Microsoft",
                        label="ORGANIZATION",
                        parent="OpenAI",
                        children=[],
                    )
                ],
            ),
            NestedEntity(
                entity="Facebook AI Research",
                label="ORGANIZATION",
                parent=None,
                children=[
                    NestedEntity(
                        entity="Meta Platforms Inc.",
                        label="ORGANIZATION",
                        parent="Facebook AI Research",
                        children=[],
                    )
                ],
            ),
            NestedEntity(
                entity="Meta Platforms Inc.",
                label="ORGANIZATION",
                parent=None,
                children=[],
            ),
            NestedEntity(
                entity="Microsoft", label="ORGANIZATION", parent=None, children=[]
            ),
        ],
    ),
]


@pytest.mark.parametrize("text,expected_output", test_cases)
def test_nested_ner(text: str, expected_output: list[NestedEntity]):
    output = nested_ner(text)
    assert len(output) == len(expected_output)
    for entity, expected_entity in zip(output, expected_output, strict=False):
        assert entity.model_dump() == expected_entity.model_dump()


ipytest.run()  # Run the tests in Jupyter Notebook
```


It's important to heavily test any system before you put it in practice. The above example demonstrates how to test such a method (`nested_ner` in this case), but it only shows a single input/output pair for brevity.

We strongly encourage you to write far more robust tests in your applications with many more test cases. This is why our examples uses `@pytest.mark.parametrize` to easily include additional test cases.

## Further Improvements

This Named Entity Recognition (NER) system leverages the power of LLMs to perform context-aware, hierarchical entity extraction with various levels of nesting. It can identify complex relationships between entities, making it suitable for a wide range of applications.

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Information Extraction</b>: Extracting structured information from unstructured text data.</li>
<li><b>Question Answering</b>: Identifying entities relevant to a given question.</li>
<li><b>Document Summarization</b>: Summarizing documents by extracting key entities and relationships.</li>
<li><b>Sentiment Analysis</b>: Analyzing sentiment towards specific entities or topics.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider the following:

- Prompt customization to guide the model towards specific entity types or relationships.
- Fine-tuning the model on domain-specific data for better accuracy in particular fields.
- Implementing a confidence score for each identified entity.
- Integrating with a knowledge base to enhance entity disambiguation.
- Developing a post-processing step to refine and validate the LLM's output.
- Exploring ways to optimize performance for real-time applications.

By leveraging the power of LLMs and the flexibility of the Mirascope library, you can create sophisticated NER systems that go beyond traditional approaches, enabling more nuanced and context-aware entity recognition for various applications.

