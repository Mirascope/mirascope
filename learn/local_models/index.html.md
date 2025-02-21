---
search:
  boost: 3
---

# Local (Open-Source) Models

When hosting (fine-tuned) open-source LLMs yourself locally or in your own cloud with tools that have OpenAI compatibility (e.g. [Ollama](https://github.com/ollama/ollama), [vLLM](https://github.com/vllm-project/vllm), etc.), you can use the [`openai.call`](../api/core/openai/call.md) method with a [custom client](./calls.md#custom-client) to interact with your model using all of Mirascope's various features.

Of course, not all open-source models or providers necessarily support all of OpenAI's available features, but most use-cases are generally available. Se the links we've included in each usage example below for more details.

!!! mira ""

    === "Ollama"

        !!! info ""

            [Ollama OpenAI Compatibility](https://github.com/ollama/ollama/blob/main/docs/openai.md)

        ```python hl_lines="5-8 11 26"
            from mirascope.core import openai
            from openai import OpenAI
            from pydantic import BaseModel

            custom_client = OpenAI(
                base_url="http://localhost:11434/v1",  # your ollama endpoint
                api_key="unused",  # required by openai, but unused
            )


            @openai.call("llama3.2", client=custom_client)
            def recommend_book(genre: str) -> str:
                return f"Recommend a {genre} book"


            recommendation = recommend_book("fantasy")
            print(recommendation)
            # Output: Here are some popular and highly-recommended fantasy books...


            class Book(BaseModel):
                title: str
                author: str


            @openai.call("llama3.2", response_model=Book, client=custom_client)
            def extract_book(text: str) -> str:
                return f"Extract {text}"


            book = extract_book("The Name of the Wind by Patrick Rothfuss")
            assert isinstance(book, Book)
            print(book)
            # Output: title='The Name of the Wind' author='Patrick Rothfuss'
        ```
    
    === "vLLM"

        !!! info ""

            [vLLM OpenAI Compatibility](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html)

        ```python hl_lines="5-8 11 26"
            from mirascope.core import openai
            from openai import OpenAI
            from pydantic import BaseModel

            custom_client = OpenAI(
                base_url="http://localhost:8000/v1",  # your vLLM endpoint
                api_key="unused",  # required by openai, but unused
            )


            @openai.call("llama3.2", client=custom_client)
            def recommend_book(genre: str) -> str:
                return f"Recommend a {genre} book"


            recommendation = recommend_book("fantasy")
            print(recommendation)
            # Output: Here are some popular and highly-recommended fantasy books...


            class Book(BaseModel):
                title: str
                author: str


            @openai.call("llama3.2", response_model=Book, client=custom_client)
            def extract_book(text: str) -> str:
                return f"Extract {text}"


            book = extract_book("The Name of the Wind by Patrick Rothfuss")
            assert isinstance(book, Book)
            print(book)
            # Output: title='The Name of the Wind' author='Patrick Rothfuss'
        ```
    
