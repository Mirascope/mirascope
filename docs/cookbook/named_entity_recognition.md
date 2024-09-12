# Named Entity Recognition

In this guide, we demonstrate techniques to perform Named Entity Recognition (NER) using Large Language Models (LLMs). We will use Groq's llama-3.1-8b-instant model, but you can adapt this approach to other models with similar capabilities.

??? tip "Mirascope Concepts Used"

    - [Calls](../learn/calls.md)
    - [Response Model](../learn/response_models.md)
    - [Prompt Templates](../learn/prompt_templates.md)

!!! note "Background"

    Named Entity Recognition is a subtask of information extraction that seeks to locate and classify named entities in text into predefined categories such as person names, organizations, locations, etc. LLMs have revolutionized NER by enabling more context-aware and hierarchical entity recognition, going beyond traditional rule-based or statistical methods.

## Setup and Imports

First, let's set up our environment with the necessary imports:

```python
from mirascope.core import groq, prompt_template
from pydantic import BaseModel, Field
from typing import List, Optional
```

## Defining Data Models

We'll use Pydantic models to structure our entity data:

```python
class NamedEntity(BaseModel):
    entity: str = Field(description="The entity found in the text")
    label: str = Field(description="The label of the entity (e.g., PERSON, ORGANIZATION, LOCATION)")
    parent: Optional[str] = Field(description="The parent entity if this entity is nested within another entity", default=None)
    children: List['NamedEntity'] = Field(default_factory=list, description="Nested entities within this entity")

class NamedEntityRecognition(BaseModel):
    entities: List[NamedEntity] = Field(description="List of top-level named entities found in the text")
    given_text: str = Field(description="The text that was checked for named entities")
```

These models allow us to capture hierarchical relationships between entities, which is a key feature of this advanced NER approach.

## Implementing the NER Function

Now, let's create our main NER function using Groq's LLM:

```python
@groq.groq_call(
    model="llama-3.1-8b-instant",
    response_model=NamedEntityRecognition,
    json_mode=True,
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
def recognize_entities(text: str): ...
```

This function uses a prompt template to guide the LLM in identifying entities and their relationships. The `@groq.groq_call` decorator specifies the model to use and the expected response format.

## Utility Function for Printing Entity Trees

To visualize the hierarchical structure of entities, we'll use a recursive printing function:

```python
def print_entity_tree(entity, level=0):
    indent = "  " * level
    print(f"{indent}Entity: {entity.entity}, Label: {entity.label}, Parent: {entity.parent}")
    for child in entity.children:
        print_entity_tree(child, level + 1)
```

## Example Usage

Here's an example of how to use the NER system:

```python
text = """
The renowned physicist Dr. Alice Johnson, a professor at the prestigious Massachusetts Institute of Technology (MIT),
recently published a groundbreaking paper in collaboration with her colleague Dr. Bob Smith from Stanford University.
Their work, funded by the National Science Foundation (NSF), explores the intersection of quantum mechanics and
artificial intelligence. The research was conducted at the Advanced Quantum Research Center, a joint venture between
MIT and Google's AI division, located in the heart of Silicon Valley.
"""

response = recognize_entities(text)
for entity in response.entities:
    print_entity_tree(entity)
print("\nGiven Text:")
print(response.given_text)
```

## Testing with Various Scenarios

To ensure robustness, it's crucial to test the NER system with diverse scenarios. Here's a function to run multiple test cases:

```python
def test_ner_system(recognize_entities_func):
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        response = recognize_entities_func(test_case)
        for entity in response.entities:
            print_entity_tree(entity)
        print("\nGiven Text:")
        print(response.given_text)
        print("\n" + "=" * 50)

# Usage:
test_ner_system(recognize_entities)
```

The `test_cases` list contains various scenarios covering different domains and entity complexities, such as business and technology, politics and international relations, sports and entertainment, science and academia, complex nested entities, and historical and cultural references.

## Conclusion and Further Improvements

This Named Entity Recognition system leverages the power of LLMs to perform context-aware, hierarchical entity extraction. It can identify complex relationships between entities, making it suitable for a wide range of applications.

For further improvements, consider:

1. Fine-tuning the model on domain-specific data for better accuracy in particular fields.
2. Implementing a confidence score for each identified entity.
3. Integrating with a knowledge base to enhance entity disambiguation.
4. Developing a post-processing step to refine and validate the LLM's output.
5. Exploring ways to optimize performance for real-time applications.

By iterating on this foundation, you can create a powerful NER system tailored to your specific needs.

### Full Code Example

```python
from mirascope.core import groq, prompt_template
from pydantic import BaseModel, Field
from typing import List, Optional

class NamedEntity(BaseModel):
    entity: str = Field(description="The entity found in the text")
    label: str = Field(description="The label of the entity (e.g., PERSON, ORGANIZATION, LOCATION)")
    parent: Optional[str] = Field(description="The parent entity if this entity is nested within another entity", default=None)
    children: List['NamedEntity'] = Field(default_factory=list, description="Nested entities within this entity")

class NamedEntityRecognition(BaseModel):
    entities: List[NamedEntity] = Field(description="List of top-level named entities found in the text")
    given_text: str = Field(description="The text that was checked for named entities")

@groq.groq_call(
    model="llama-3.1-8b-instant",
    response_model=NamedEntityRecognition,
    json_mode=True,
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
def recognize_entities(text: str): ...

def print_entity_tree(entity, level=0):
    indent = "  " * level
    print(f"{indent}Entity: {entity.entity}, Label: {entity.label}, Parent: {entity.parent}")
    for child in entity.children:
        print_entity_tree(child, level + 1)

text = """
The renowned physicist Dr. Alice Johnson, a professor at the prestigious Massachusetts Institute of Technology (MIT),
recently published a groundbreaking paper in collaboration with her colleague Dr. Bob Smith from Stanford University.
Their work, funded by the National Science Foundation (NSF), explores the intersection of quantum mechanics and
artificial intelligence. The research was conducted at the Advanced Quantum Research Center, a joint venture between
MIT and Google's AI division, located in the heart of Silicon Valley.
"""

response = recognize_entities(text)
for entity in response.entities:
    print_entity_tree(entity)
print("\nGiven Text:")
print(response.given_text)


test_cases = [
    # Case 1: Business and Technology
    """
    Elon Musk, the CEO of Tesla and SpaceX, announced a new partnership with Microsoft's
    Azure cloud division. The collaboration aims to enhance Tesla's autonomous driving capabilities
    using Microsoft's advanced AI algorithms. The announcement was made at the annual
    TechCrunch Disrupt conference in San Francisco.
    """,

    # Case 2: Politics and International Relations
    """
    The United Nations Security Council, led by its current president Ambassador Maria Rodriguez
    from Argentina, convened an emergency meeting to address the ongoing conflict in the
    disputed region of Nagorno-Karabakh. Representatives from Armenia and Azerbaijan were
    present, along with observers from the OSCE Minsk Group co-chairs: France, Russia, and
    the United States.
    """,

    # Case 3: Sports and Entertainment
    """
    LeBron James, star player for the Los Angeles Lakers, has signed a lucrative endorsement
    deal with Nike's Jordan Brand, a subsidiary of Nike Inc. The deal, negotiated by James's
    agent Rich Paul of Klutch Sports Group, is reportedly worth over $1 billion. The
    announcement was made at the Staples Center in Los Angeles, home to both the Lakers
    and the LA Clippers.
    """,

    # Case 4: Science and Academia
    """
    Dr. Jennifer Lee, a molecular biologist at the University of California, Berkeley,
    has received the prestigious Nobel Prize in Chemistry for her groundbreaking work on
    CRISPR gene editing. Her research, conducted in collaboration with the Howard Hughes
    Medical Institute and the Max Planck Institute for Molecular Genetics in Berlin, has
    opened new avenues for treating genetic disorders.
    """,

    # Case 5: Complex Nested Entities
    """
    The multinational conglomerate Alphabet Inc., parent company of Google, has acquired
    DeepMind, a leading AI research laboratory based in London. DeepMind's founder,
    Demis Hassabis, will join Google Brain, a division of Google AI, as Chief AI Scientist.
    This move strengthens Alphabet's position in the AI field, challenging competitors like
    OpenAI, which is backed by Microsoft, and Facebook AI Research, a part of Meta Platforms Inc.
    """,

    # Case 6: Historical and Cultural References
    """
    The Louvre Museum in Paris, home to Leonardo da Vinci's Mona Lisa, has partnered with
    the British Museum in London for a joint exhibition on ancient civilizations. The exhibit
    will feature artifacts from the Egyptian Old Kingdom, including items from the tomb of
    Pharaoh Khufu, builder of the Great Pyramid of Giza. Curators from both institutions,
    led by Dr. Sophie Martin of the Louvre and Professor John Williams of the British Museum,
    have collaborated on this unprecedented cultural exchange.
    """,
]

# Function to test the NER system with all cases
def test_ner_system(recognize_entities_func):
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        response = recognize_entities_func(test_case)
        for entity in response.entities:
            print_entity_tree(entity)
        print("\nGiven Text:")
        print(response.given_text)
        print("\n" + "=" * 50)

# Usage:
test_ner_system(recognize_entities)

# Expected Output:
"""
Entity: Dr. Alice Johnson, Label: PERSON, Parent: None
  Entity: Massachusetts Institute of Technology (MIT), Label: ORGANIZATION, Parent: Dr. Alice Johnson
    Entity: National Science Foundation (NSF), Label: ORGANIZATION, Parent: Massachusetts Institute of Technology (MIT)
    Entity: Advanced Quantum Research Center, Label: ORGANIZATION, Parent: Massachusetts Institute of Technology (MIT)
      Entity: Google's AI division, Label: ORGANIZATION, Parent: Advanced Quantum Research Center
  Entity: Stanford University, Label: ORGANIZATION, Parent: Dr. Alice Johnson
Entity: Silicon Valley, Label: LOCATION, Parent: None
Entity: Dr. Bob Smith, Label: PERSON, Parent: None
  Entity: Stanford University, Label: ORGANIZATION, Parent: Dr. Bob Smith
Entity: National Science Foundation (NSF), Label: ORGANIZATION, Parent: None

Given Text:
The renowned physicist Dr. Alice Johnson, a professor at the prestigious Massachusetts Institute of Technology (MIT),
recently published a groundbreaking paper in collaboration with her colleague Dr. Bob Smith from Stanford University.
Their work, funded by the National Science Foundation (NSF), explores the intersection of quantum mechanics and
artificial intelligence. The research was conducted at the Advanced Quantum Research Center, a joint venture between
MIT and Google's AI division, located in the heart of Silicon Valley.

--- Test Case 1 ---
Entity: Elon Musk, Label: PERSON, Parent: None
  Entity: Tesla, Label: ORGANIZATION, Parent: Elon Musk
    Entity: SpaceX, Label: ORGANIZATION, Parent: Tesla
Entity: Microsoft, Label: ORGANIZATION, Parent: None
  Entity: Azure, Label: LOCATION, Parent: Microsoft
Entity: TechCrunch Disrupt, Label: EVENT, Parent: None
  Entity: San Francisco, Label: LOCATION, Parent: TechCrunch Disrupt
Entity: San Francisco, Label: LOCATION, Parent: None

Given Text:
Elon Musk, the CEO of Tesla and SpaceX, announced a new partnership with Microsoft's Azure cloud division. The collaboration aims to enhance Tesla's autonomous driving capabilities using Microsoft's advanced AI algorithms. The announcement was made at the annual TechCrunch Disrupt conference in San Francisco.

==================================================

--- Test Case 2 ---
Entity: The United Nations Security Council, Label: ORGANIZATION, Parent: None
  Entity: Security Council, Label: ORGANIZATION, Parent: The United Nations Security Council
Entity: Ambassador Maria Rodriguez, Label: PERSON, Parent: None
  Entity: Maria Rodriguez, Label: PERSON, Parent: Ambassador Maria Rodriguez
Entity: Argentina, Label: LOCATION, Parent: None
Entity: Nagorno-Karabakh, Label: LOCATION, Parent: None
Entity: Armenia, Label: LOCATION, Parent: None
Entity: Azerbaijan, Label: LOCATION, Parent: None
Entity: OSCE Minsk Group, Label: ORGANIZATION, Parent: None
  Entity: Minsk Group, Label: ORGANIZATION, Parent: OSCE Minsk Group
Entity: France, Label: LOCATION, Parent: None
Entity: Russia, Label: LOCATION, Parent: None
Entity: The United States, Label: LOCATION, Parent: None
Entity: Ambassador, Label: TITLE, Parent: None
  Entity: United Nations Security Council, Label: ORGANIZATION, Parent: Ambassador

Given Text:
The United Nations Security Council, led by its current president Ambassador Maria Rodriguez from Argentina, convened an emergency meeting to address the ongoing conflict in the disputed region of Nagorno-Karabakh. Representatives from Armenia and Azerbaijan were present, along with observers from the OSCE Minsk Group co-chairs: France, Russia, and the United States.

==================================================

--- Test Case 3 ---
Entity: LeBron James, Label: PERSON, Parent: None
  Entity: Los Angeles Lakers, Label: ORGANIZATION, Parent: LeBron James
    Entity: Los Angeles, Label: LOCATION, Parent: Los Angeles Lakers
  Entity: Nike, Label: ORGANIZATION, Parent: None
    Entity: Nike's Jordan Brand, Label: ORGANIZATION, Parent: Nike
  Entity: Klutch Sports Group, Label: ORGANIZATION, Parent: None
    Entity: Rich Paul, Label: PERSON, Parent: Klutch Sports Group
Entity: Nike Inc., Label: ORGANIZATION, Parent: Nike's Jordan Brand
Entity: Staples Center, Label: LOCATION, Parent: None
  Entity: Los Angeles, Label: LOCATION, Parent: Staples Center
Entity: LA Clippers, Label: ORGANIZATION, Parent: None
  Entity: Los Angeles, Label: LOCATION, Parent: LA Clippers

Given Text:
LeBron James, star player for the Los Angeles Lakers, has signed a lucrative endorsement deal with Nike's Jordan Brand, a subsidiary of Nike Inc. The deal, negotiated by James's agent Rich Paul of Klutch Sports Group, is reportedly worth over $1 billion. The announcement was made at the Staples Center in Los Angeles, home to both the Lakers and the LA Clippers.

==================================================

--- Test Case 4 ---
Entity: Dr. Jennifer Lee, Label: PERSON, Parent: None
  Entity: University of California, Berkeley, Label: ORGANIZATION, Parent: Dr. Jennifer Lee
    Entity: Berkeley, Label: LOCATION, Parent: University of California, Berkeley
Entity: Nobel Prize in Chemistry, Label: ORGANIZATION/AWARD, Parent: None
Entity: CRISPR gene editing, Label: FIELD OF STUDY, Parent: None
Entity: Howard Hughes Medical Institute, Label: ORGANIZATION, Parent: None
Entity: Max Planck Institute for Molecular Genetics, Label: ORGANIZATION, Parent: None
  Entity: Berlin, Label: LOCATION, Parent: Max Planck Institute for Molecular Genetics

Given Text:
Dr. Jennifer Lee, a molecular biologist at the University of California, Berkeley, has received the prestigious Nobel Prize in Chemistry for her groundbreaking work on CRISPR gene editing. Her research, conducted in collaboration with the Howard Hughes Medical Institute and the Max Planck Institute for Molecular Genetics in Berlin, has opened new avenues for treating genetic disorders.

==================================================

--- Test Case 5 ---
Entity: Alphabet Inc., Label: ORGANIZATION, Parent: None
  Entity: Google, Label: ORGANIZATION, Parent: Alphabet Inc.
    Entity: Google AI, Label: ORGANIZATION, Parent: Google
      Entity: Google Brain, Label: ORGANIZATION, Parent: Google AI
Entity: DeepMind, Label: ORGANIZATION, Parent: None
  Entity: London, Label: LOCATION, Parent: DeepMind
  Entity: Demis Hassabis, Label: PERSON, Parent: DeepMind
    Entity: DeepMind, Label: ORGANIZATION, Parent: Demis Hassabis
Entity: Google, Label: ORGANIZATION, Parent: Alphabet Inc.
  Entity: Google AI, Label: ORGANIZATION, Parent: None
Entity: OpenAI, Label: ORGANIZATION, Parent: None
  Entity: Microsoft, Label: ORGANIZATION, Parent: OpenAI
Entity: Facebook AI Research, Label: ORGANIZATION, Parent: None
  Entity: Meta Platforms Inc., Label: ORGANIZATION, Parent: Facebook AI Research

Given Text:
The multinational conglomerate Alphabet Inc., parent company of Google, has acquired DeepMind, a leading AI research laboratory based in London. DeepMind's founder, Demis Hassabis, will join Google Brain, a division of Google AI, as Chief AI Scientist. This move strengthens Alphabet's position in the AI field, challenging competitors like OpenAI, which is backed by Microsoft, and Facebook AI Research, a part of Meta Platforms Inc.

==================================================

--- Test Case 6 ---
Entity: The Louvre Museum, Label: ORGANIZATION, Parent: None
  Entity: Paris, Label: LOCATION, Parent: The Louvre Museum
  Entity: Leonardo da Vinci, Label: PERSON, Parent: None
    Entity: Mona Lisa, Label: WORK_OF_ART, Parent: Leonardo da Vinci
Entity: The British Museum, Label: ORGANIZATION, Parent: None
  Entity: London, Label: LOCATION, Parent: The British Museum
  Entity: Professor John Williams, Label: PERSON, Parent: The British Museum
Entity: Dr. Sophie Martin, Label: PERSON, Parent: None
Entity: Egyptian Old Kingdom, Label: EVENT, Parent: None
Entity: Pharaoh Khufu, Label: PERSON, Parent: None
  Entity: The Great Pyramid of Giza, Label: STRUCTURE, Parent: Pharaoh Khufu

Given Text:
The Louvre Museum in Paris, home to Leonardo da Vinci's Mona Lisa, has partnered with the British Museum in London for a joint exhibition on ancient civilizations. The exhibit will feature artifacts from the Egyptian Old Kingdom, including items from the tomb of Pharaoh Khufu, builder of the Great Pyramid of Giza. Curators from both institutions, led by Dr. Sophie Martin of the Louvre and Professor John Williams of the British Museum, have collaborated on this unprecedented cultural exchange.

==================================================
"""
```
