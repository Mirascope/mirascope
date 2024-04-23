# Llama Index

Since Mirascope RAG is plug-and-play, you can easily use Llama Index for all of your RAG needs while still taking advantage of everything else Mirascope has to offer.

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from mirascope.anthropic import AnthropicCall

# Load documents and build index
documents = SimpleDirectoryReader("./paul_graham_essays").load_data()
retriever = VectorStoreIndex.from_documents(documents).as_retriever()

# Create Paul Graham Bot
class PaulGrahamBot(AnthropicCall):
    prompt_template = """
    SYSTEM:
    Your task is to respond to the user as though you are Paul Graham.

    Here are some excerpts from Paul Graham's essays relevant to the user query.
    Use them as a reference for how to respond.

    <excerpts>
    {excerpts}
    </excepts>
    """

    query: str = ""

    @property
    def excerpts(self) -> list[str]:
        """Retrieves excerpts from Paul Graham's essays relevant to `query`."""
        return [node.get_content() for node in retriever.retrieve(self.query)]


pg = PaulGrahamBot()
pg.query = input("User: ")
response = pg.call()
print(response.content)
```
