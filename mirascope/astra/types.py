from pydantic import BaseModel
from typing import Any, Optional, Literal

class AstraSettings(BaseModel):
    api_endpoint: str = "astra_endpoint"
    application_token: str = "token_here"
    collection_name: str = "default_collection"

class AstraParams(BaseModel):
    # Additional parameters can be added here as needed.
    pass

class AstraQueryResult(BaseModel):
    documents: Optional[list[list[str]]] = None

    @staticmethod
    def convert(api_response):
        return AstraQueryResult(
            documents=[
                {"text": result["text"], "source": result["source"]}
                for result in api_response
            ]
        )
