from __future__ import annotations

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
@prompt_template("Extract the entities from this text: {text}")
def simple_ner(text: str): ...


print("Simple NER Results:")
simple_result = simple_ner(unstructured_text)
for entity in simple_result:
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

# Output
"""
Nested NER Results:
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

import pytest  # noqa: E402

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
            NestedEntity(
                entity="Demis Hassabis", label="PERSON", parent=None, children=[]
            ),
            NestedEntity(entity="London", label="LOCATION", parent=None, children=[]),
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
                entity="Microsoft", label="ORGANIZATION", parent=None, children=[]
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
        ],
    ),
]


@pytest.mark.parametrize("text,expected_output", test_cases)
def test_nested_ner(text: str, expected_output: list[NestedEntity]):
    output = nested_ner(text)
    assert len(output) == len(expected_output)
    for entity, expected_entity in zip(output, expected_output, strict=False):
        assert entity.model_dump() == expected_entity.model_dump()
