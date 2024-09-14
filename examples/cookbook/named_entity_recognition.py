from mirascope.core import groq, prompt_template
from pydantic import BaseModel, Field
from typing import List, Optional
import textwrap

call_params = groq.GroqCallParams(temperature=0.0)

class SimpleEntity(BaseModel):
    entity: str = Field(description="The entity found in the text")
    label: str = Field(description="The label of the entity (e.g., PERSON, ORGANIZATION, LOCATION)")

class SimpleNER(BaseModel):
    entities: List[SimpleEntity] = Field(description="List of named entities found in the text")

@groq.call(
    model="llama-3.1-8b-instant",
    response_model=SimpleNER,
    json_mode=True,
    call_params=call_params,
)
@prompt_template(
    """
    Extract the entities from this text: {text}
    """
)
def simple_ner(text: str): ...

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
    call_params=call_params,
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

print("Simple NER Results:")
simple_result = simple_ner(complex_text)
for entity in simple_result.entities:
    print(f"Entity: {entity.entity}, Label: {entity.label}")

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
    # Additional Test Cases for different nesting levels
    # Case 7: Single Entity
    "Elon Musk, the CEO of Tesla and SpaceX, announced a new partnership with Microsoft's Azure cloud division.",
    
    # Case 8: Multiple Entities at Different Levels
    "The United Nations Security Council, led by its current president Ambassador Maria Rodriguez from Argentina, convened an emergency meeting.",
    
    # Case 9: Nested Entities with Multiple Children
    "Apple Inc., founded by Steve Jobs and currently led by Tim Cook, is headquartered in Cupertino, California, and is known for products like the iPhone and MacBook."
]

def print_entity_tree(entity, level=0):
    indent = "  " * level
    entity_info = f"Entity: {entity.entity}, Label: {entity.label}, Parent: {entity.parent}"
    print(textwrap.indent(entity_info, indent))
    for child in entity.children:
        print_entity_tree(child, level + 1)
        
# Function to test the NER system with all cases
def test_ner_system(recognize_entities_func):
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        response = recognize_entities_func(test_case)
        for entity in response.entities:
            print_entity_tree(entity)
        print("\n" + "=" * 50)

# Usage:
test_ner_system(improved_ner)