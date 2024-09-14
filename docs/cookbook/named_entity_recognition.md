# Named Entity Recognition

This guide demonstrates techniques to perform Named Entity Recognition (NER) using Large Language Models (LLMs) with various levels of nested entity recognition. We'll use Groq's llama-3.1-8b-instant model, but you can adapt this approach to other models with similar capabilities.

??? tip "Mirascope Concepts Used"

    - [Calls](../learn/calls.md)
    - [Response Model](../learn/response_models.md)
    - [Prompt Templates](../learn/prompt_templates.md)

## Background

Named Entity Recognition is a subtask of information extraction that seeks to locate and classify named entities in text into predefined categories such as person names, organizations, locations, etc. LLMs have revolutionized NER by enabling more context-aware and hierarchical entity recognition, going beyond traditional rule-based or statistical methods.

## Setup

First, ensure you have the necessary packages installed and API keys set:

```bash
pip install mirascope
```

Set your Groq API key as an environment variable:

```bash
export GROQ_API_KEY=your_api_key_here
```

## Implementation

We'll implement NER with different levels of complexity: simple and nested entity recognition. Let's start with the simple version:

### Simple NER

```python
from mirascope.core import groq, prompt_template
from pydantic import BaseModel, Field
from typing import List

class SimpleEntity(BaseModel):
    entity: str = Field(description="The entity found in the text")
    label: str = Field(description="The label of the entity (e.g., PERSON, ORGANIZATION, LOCATION)")

class SimpleNER(BaseModel):
    entities: List[SimpleEntity] = Field(description="List of named entities found in the text")

@groq.call(
    model="llama-3.1-8b-instant",
    response_model=SimpleNER,
    json_mode=True,
    call_params=groq.GroqCallParams(temperature=0.0),
)
@prompt_template(
    """
    Extract the entities from this text: {text}
    """
)
def simple_ner(text: str): ...

complex_text = """
Apple Inc., the tech giant founded by Steve Jobs and Steve Wozniak, recently announced a partnership with OpenAI, the artificial intelligence research laboratory consisting of the for-profit corporation OpenAI LP and its parent company, the non-profit OpenAI Inc. This collaboration aims to enhance Siri, Apple's virtual assistant, which competes with Amazon's Alexa and Google Assistant, a product of Alphabet Inc.'s Google division. The joint project will be led by Apple's AI chief John Giannandrea, a former Google executive, and will take place at Apple Park, the company's headquarters in Cupertino, California.
"""
print("Simple NER Results:")
simple_result = simple_ner(complex_text)
for entity in simple_result.entities:
    print(f"Entity: {entity.entity}, Label: {entity.label}")

# Output
"""
Simple NER Results:
Entity: Apple Inc., Label: ORGANIZATION
Entity: Steve Jobs, Label: PERSON
Entity: Steve Wozniak, Label: PERSON
Entity: OpenAI, Label: ORGANIZATION
Entity: OpenAI LP, Label: ORGANIZATION
Entity: OpenAI Inc., Label: ORGANIZATION
Entity: Amazon, Label: ORGANIZATION
Entity: Alexa, Label: PRODUCT
Entity: Google, Label: ORGANIZATION
Entity: Alphabet Inc., Label: ORGANIZATION
Entity: John Giannandrea, Label: PERSON
Entity: Apple Park, Label: LOCATION
Entity: Cupertino, Label: LOCATION
Entity: California, Label: LOCATION
"""
```

### Nested NER

Now, let's implement a more sophisticated version that can handle nested entities:

```python
from typing import Optional

class NestedEntity(BaseModel):
    entity: str = Field(description="The entity found in the text")
    label: str = Field(description="The label of the entity (e.g., PERSON, ORGANIZATION, LOCATION)")
    parent: Optional[str] = Field(description="The parent entity if this entity is nested within another entity", default=None)
    children: List['NestedEntity'] = Field(default_factory=list, description="Nested entities within this entity")

class ImprovedNER(BaseModel):
    entities: List[NestedEntity] = Field(description="List of top-level named entities found in the text")

@groq.call(
    model="llama-3.1-8b-instant",
    response_model=ImprovedNER,
    json_mode=True,
    call_params=groq.GroqCallParams(temperature=0.0),
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

    Now, analyze the following text:

    Text: {text}
    """
)
def improved_ner(text: str): ...

complex_text = """
Apple Inc., the tech giant founded by Steve Jobs and Steve Wozniak, recently announced a partnership with OpenAI, the artificial intelligence research laboratory consisting of the for-profit corporation OpenAI LP and its parent company, the non-profit OpenAI Inc. This collaboration aims to enhance Siri, Apple's virtual assistant, which competes with Amazon's Alexa and Google Assistant, a product of Alphabet Inc.'s Google division. The joint project will be led by Apple's AI chief John Giannandrea, a former Google executive, and will take place at Apple Park, the company's headquarters in Cupertino, California.
"""
print("\nImproved NER Results:")
improved_result = improved_ner(complex_text)

def print_nested_entities(entities, level=0):
    for entity in entities:
        indent = "  " * level
        entity_info = f"Entity: {entity.entity}, Label: {entity.label}, Parent: {entity.parent}"
        print(textwrap.indent(entity_info, indent))
        if entity.children:
            print_nested_entities(entity.children, level + 1)

print_nested_entities(improved_result.entities)

# Output
"""
Improved NER Results:
Entity: Apple Inc., Label: ORGANIZATION, Parent: None
  Entity: Steve Jobs, Label: PERSON, Parent: Apple Inc.
  Entity: Steve Wozniak, Label: PERSON, Parent: Apple Inc.
  Entity: OpenAI, Label: ORGANIZATION, Parent: Apple Inc.
    Entity: OpenAI LP, Label: ORGANIZATION, Parent: OpenAI
      Entity: OpenAI Inc., Label: ORGANIZATION, Parent: OpenAI LP
  Entity: John Giannandrea, Label: PERSON, Parent: Apple Inc.
  Entity: Apple Park, Label: LOCATION, Parent: Apple Inc.
  Entity: Cupertino, Label: LOCATION, Parent: Apple Park
  Entity: California, Label: LOCATION, Parent: Cupertino
Entity: OpenAI LP, Label: ORGANIZATION, Parent: OpenAI
Entity: OpenAI Inc., Label: ORGANIZATION, Parent: OpenAI LP
Entity: Alphabet Inc., Label: ORGANIZATION, Parent: None
  Entity: Google, Label: ORGANIZATION, Parent: Alphabet Inc.
    Entity: Google Assistant, Label: ORGANIZATION, Parent: Google
Entity: Amazon, Label: ORGANIZATION, Parent: None
  Entity: Alexa, Label: ORGANIZATION, Parent: Amazon
"""
```

## Utility Functions

To help visualize the hierarchical structure of entities, we can use a recursive printing function:

```python
import textwrap

def print_entity_tree(entity, level=0):
    indent = "  " * level
    entity_info = f"Entity: {entity.entity}, Label: {entity.label}, Parent: {entity.parent}"
    print(textwrap.indent(entity_info, indent))
    for child in entity.children:
        print_entity_tree(child, level + 1)
```

## Testing

To ensure robustness, it's crucial to test the NER system with diverse scenarios. Here's a function to run multiple test cases:

```python
def test_ner_system(recognize_entities_func):
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        response = recognize_entities_func(test_case)
        for entity in response.entities:
            print_entity_tree(entity)
        print("\n" + "=" * 50)

# Define test cases
test_cases = [
    "Elon Musk, the CEO of Tesla and SpaceX, announced a new partnership with Microsoft's Azure cloud division.",
    "The United Nations Security Council, led by its current president Ambassador Maria Rodriguez from Argentina, convened an emergency meeting.",
    "Apple Inc., founded by Steve Jobs and currently led by Tim Cook, is headquartered in Cupertino, California, and is known for products like the iPhone and MacBook."
]

# Run tests
test_ner_system(improved_ner)

# Output
"""
--- Test Case 1 ---
Entity: Elon Musk, Label: PERSON, Parent: None
  Entity: Tesla, Label: ORGANIZATION, Parent: Elon Musk
    Entity: SpaceX, Label: ORGANIZATION, Parent: Tesla
Entity: Microsoft, Label: ORGANIZATION, Parent: None
  Entity: Azure, Label: ORGANIZATION, Parent: Microsoft

==================================================

--- Test Case 2 ---
Entity: United Nations Security Council, Label: ORGANIZATION, Parent: None
  Entity: United Nations, Label: ORGANIZATION, Parent: United Nations Security Council
  Entity: Security Council, Label: ORGANIZATION, Parent: United Nations Security Council
Entity: Ambassador Maria Rodriguez, Label: PERSON, Parent: None
  Entity: Maria Rodriguez, Label: PERSON, Parent: Ambassador Maria Rodriguez
    Entity: Argentina, Label: LOCATION, Parent: Maria Rodriguez

==================================================

--- Test Case 3 ---
Entity: Apple Inc., Label: ORGANIZATION, Parent: None
  Entity: Steve Jobs, Label: PERSON, Parent: Apple Inc.
  Entity: Tim Cook, Label: PERSON, Parent: Apple Inc.
Entity: Cupertino, Label: LOCATION, Parent: Apple Inc.
Entity: California, Label: LOCATION, Parent: Cupertino
Entity: iPhone, Label: PRODUCT, Parent: Apple Inc.
Entity: MacBook, Label: PRODUCT, Parent: Apple Inc.

==================================================
```
```

## Further Improvements

This Named Entity Recognition system leverages the power of LLMs to perform context-aware, hierarchical entity extraction with various levels of nesting. It can identify complex relationships between entities, making it suitable for a wide range of applications.

!!! tip "Additional Real-World Applications"

    - **Information Extraction**: Extracting structured information from unstructured text data.
    - **Question Answering**: Identifying entities relevant to a given question.
    - **Document Summarization**: Summarizing documents by extracting key entities and relationships.
    - **Sentiment Analysis**: Analyzing sentiment towards specific entities or topics.

When adapting this recipe to your specific use-case, consider the following:

- Prompt customization to guide the model towards specific entity types or relationships.
- Fine-tuning the model on domain-specific data for better accuracy in particular fields.
- Implementing a confidence score for each identified entity.
- Integrating with a knowledge base to enhance entity disambiguation.
- Developing a post-processing step to refine and validate the LLM's output.
- Exploring ways to optimize performance for real-time applications.

By leveraging the power of LLMs and the flexibility of the Mirascope library, you can create sophisticated NER systems that go beyond traditional approaches, enabling more nuanced and context-aware entity recognition for various applications.
