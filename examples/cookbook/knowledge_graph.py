import matplotlib.pyplot as plt
import networkx as nx
from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template


class Edge(BaseModel):
    source: str = Field(..., description="The source node of the edge")
    target: str = Field(..., description="The target node of the edge")
    relationship: str = Field(
        ..., description="The relationship between the source and target nodes"
    )


class Node(BaseModel):
    id: str = Field(..., description="The unique identifier of the node")
    type: str = Field(..., description="The type or label of the node")
    properties: dict | None = Field(
        ..., description="Additional properties and metadata associated with the node"
    )


class KnowledgeGraph(BaseModel):
    nodes: list[Node] = Field(..., description="List of nodes in the knowledge graph")
    edges: list[Edge] = Field(..., description="List of edges in the knowledge graph")


question = "What are the pitfalls of using LLMs?"


@openai.call(model="gpt-4o-mini", response_model=KnowledgeGraph)
@prompt_template(
    """
    SYSTEM:
    Your job is to create a knowledge graph based on the text and user question.
    
    The article:
    {text}

    Example:
    John and Jane Doe are siblings. Jane is 25 and 5 years younger than John.
    Node(id="John Doe", type="Person", properties={{"age": 30}})
    Node(id="Jane Doe", type="Person", properties={{"age": 25}})
    Edge(source="John Doe", target="Jane Doe", relationship="Siblings")

    USER:
    {question}
    """
)
def generate_knowledge_graph(
    question: str, file_name: str
) -> openai.OpenAIDynamicConfig:
    text = ""
    with open(file_name) as f:
        text = f.read()
    return {"computed_fields": {"text": text}}


kg = generate_knowledge_graph(question, "../wikipedia.txt")


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    SYSTEM:
    Answer the following question based on the knowledge graph.

    Knowledge Graph:
    {knowledge_graph}
    
    USER:
    {question}
    """
)
def run(question: str, knowledge_graph: KnowledgeGraph): ...


print(kg)
print(run(question, kg))


def render_graph(kg: KnowledgeGraph):
    G = nx.DiGraph()

    for node in kg.nodes:
        G.add_node(node.id, label=node.type, **(node.properties or {}))

    for edge in kg.edges:
        G.add_edge(edge.source, edge.target, label=edge.relationship)

    plt.figure(figsize=(15, 10))
    pos = nx.spring_layout(G)

    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="lightblue")
    nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=20)
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold")

    edge_labels = nx.get_edge_attributes(G, "label")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red")

    plt.title("Knowledge Graph Visualization", fontsize=15)
    plt.show()


question = "What are the pitfalls of using LLMs?"
render_graph(kg)
