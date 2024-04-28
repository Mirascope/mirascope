from pydantic import BaseModel
from typing import Any, Optional, Literal

class AstraSettings(BaseModel):
    api_endpoint: str = "your endpoint here"
    application_token: str = "your token here"
    collection_name: str = "your collection name here"

class AstraParams(BaseModel):
    # Additional parameters can be added here as needed.
    pass

class AstraQueryResult(BaseModel):
    documents: Optional[list[list[str]]] = None

    @staticmethod
    def convert(api_response):
        return AstraQueryResult(
            documents=[
                [f"text: {result['text']}", f"source: {result['source']}"]
                for result in api_response
            ]
        )
