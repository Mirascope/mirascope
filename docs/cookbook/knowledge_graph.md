# Knowledge Graph

Often times, data is messy and not always stored in a structured manner ready for use by an LLM. In this recipe, we show how to create a knowledge graph from an unstructured document using common python libraries and Mirascope using OpenAI GPT-4o-mini.

??? tip "Mirascope Concepts Used"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)
    - [Response Models](../learn/response_models.md)

!!! note "Background"

    While traditional Natural Language Processing (NLP) techniques have long been used in knowledge graphs to identify entities and relationships in unstructured text, Large Language Models (LLMs) have significantly improved this process. LLMs enhance the accuracy of entity identification and linking to knowledge graph entries, demonstrating superior ability to handle context and ambiguity compared to conventional NLP methods. 

## Setup

```bash
pip install mirascope[openai]
# (Optional) For visualization
pip install matplotlib networkx
```

## Create the `KnowledgeGraph`

The first step is to create a `KnowledgeGraph` with `Nodes` and `Edges` that represent our entities and relationships. For our simple recipe, we will use a Pydantic `BaseModel` to represent our `KnowledgeGraph`:

```python
--8<-- "examples/cookbook/knowledge_graph.py:3:4"
--8<-- "examples/cookbook/knowledge_graph.py:7:26"
```

Our `Edge` represents connections between nodes, with attributes for the source node, target node, and the relationship between them. While our `Node` defines nodes with an ID, type, and optional properties. Our `KnowledgeGraph` then aggregates these nodes and edges into a comprehensive knowledge graph.

Now that we have our schema defined, it's time to create our knowledge graph.

## Creating the knowledge graph

We start off with engineering our prompt, prompting the LLM to create a knowledge graph based on the user query. Then we are taking a [Wikipedia](https://en.wikipedia.org/wiki/Large_language_model) article and converting the raw text into a structured knowledge graph.

```python
--8<-- "examples/cookbook/knowledge_graph.py:5:7"
--8<-- "examples/cookbook/knowledge_graph.py:32:60"
```

We engineer our prompt by giving examples of how the properties should be filled out and use Mirascope's `DynamicConfig` to pass in the article. While it seems silly in this context, there may be multiple documents that you may want to conditionally pass in depending on the query. This can include text chunks from a Vector Store or data from a Database.

After we generated our knowledge graph, it is time to create our `run` function

```python
--8<-- "examples/cookbook/knowledge_graph.py:63:76"
```

We define a simple `run` function that answers the users query based on the knowledge graph. Combining knowledge graphs with semantic search will lead to the LLM having better context to address complex questions.

```python
--8<-- "examples/cookbook/knowledge_graph.py:80:93"
```

## Render your graph

Optionally, to visualize the knowledge graph, we use networkx and matplotlib to draw the edges and nodes.

```python
--8<-- "examples/cookbook/knowledge_graph.py:1:2"
--8<-- "examples/cookbook/knowledge_graph.py:94:120"
```

![knowledge-graph](../assets/knowledge-graph.png)

!!! tip "Additional Real-World Applications"

    1. Enhance your Q&A
        - Customer support system uses knowledge graph containing information about products to answer questions.
        - Example: "Does the Mirascope phone support fast charging?" The knowledge graph has a node "Mirascope smartphone" and searches "support" edge to find fast charging and returns results for the LLM to use.

    2. Supply Chain Optimization
        - A knowledge graph could represent complex relationships between suppliers, manufacturing plants, distribution centers, products, and transportation routes.
        - Example: How would a 20% increase in demand for a mirascope affect our inventory needs and shipping costs? Use knowledge graph to trace the mirascope toy, calculate inventory, and then estimate shipping costs and return results for the LLM to give a report.

    3. Healthcare Assistant
        - Assuming no PII or HIPPA violation, build a knowledge graph from patient remarks.
        - Example: "Mary said help, I've fallen". Build up a knowledge graph from comments and use an LLM to scan the node "Mary" for any worrying activity. Have the LLM alert Healthcare employees that there may be an emergency.

When adapting this recipe, consider:

- Combining knowledge graph with Text Embeddings for both structured search and semantic search, depending on your requirements.
- Store your knowledge graph in a database / cache for faster retrieval.
- Experiment with different LLM models, some may be better than others for generating the knowledge graph.
- Turn the example into an Agentic workflow, giving it access to tools such as web search so the LLM can call tools to update its own knowledge graph to answer any question.
- Adding Pydantic `AfterValidators` to prevent duplicate Node IDs.
