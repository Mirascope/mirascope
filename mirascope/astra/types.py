"""Types for interacting with Astra DB using Mirascope."""
from pydantic import BaseModel
from typing import Any, Optional, Literal, Dict
from .vectorstores import BaseVectorStoreParams  # Adjust import based on actual location


class AstraSettings(BaseModel):
    """
    AstraSettings stores the configuration parameters necessary to establish a connection with AstraDB.
    These parameters include the API endpoint, the application token, etc. to be used when interacting 
    with AstraDB.
    """
    token: str
    api_endpoint: str
    api_path: Optional[str] = None
    api_version: Optional[str] = None
    namespace: Optional[str] = None
    caller_name: Optional[str] = None
    caller_version: Optional[str] = None

    def kwargs(self):
        """Return a dictionary of settings suitable for passing to AstraDB client initialization."""
        return self.dict(exclude_none=True)  

class AstraParams(BaseVectorStoreParams):

    """AstraParams defines the parameters used for managing AstraDB collections.
    These can include options for collection creation, dimensions for vector search,
    metric choices, and other database-specific settings.
    
    Example usage:
params = AstraParams(
    collection_name="example_collection",
    dimension=128,
    metric="cosine",
    service_dict={"example_key": "example_value"}
)

collection = my_astra_db_instance.create_collection(
    params.collection_name,
    options=params.options,
    dimension=params.dimension,
    metric=params.metric,
    service_dict=params.service_dict,
    timeout_info=params.timeout_info
)
"""
    # Additional parameters can be added here as needed.
    collection_name: str
    options: Optional[Dict[str, Any]] = None
    dimension: Optional[int] = None
    metric: Optional[str] = None
    service_dict: Optional[Dict[str, str]] = None
    timeout_info: Optional[Any] = None  # Type here should match the expected type for timeout_info

    class Config:
        extra = "allow"  # This allows the class to accept other fields not explicitly defined here, if needed.



class AstraQueryResult(BaseModel):
    """
    AstraQueryResult defines the structure of the results returned by queries to AstraDB.
    It primarily wraps the documents retrieved as a list of lists, where each inner list
    represents a document and its associated details.

    Attributes:
        documents (Optional[list[list[str]]]): A nested list where each sublist contains
        details of a document, such as its text and source.

    Methods:
        convert(api_response: Any) -> 'AstraQueryResult':
            Converts the API response into an AstraQueryResult format, extracting relevant
            document details such as text and source from the response.
    """
    documents: Optional[list[list[str]]] = None

    @staticmethod
    def convert(api_response):
        """
        Converts a raw API response into an organized AstraQueryResult, making it easier to handle.

        Args:
            api_response (Any): The raw API response from which document details will be extracted.

        Returns:
            AstraQueryResult: The result object containing the structured documents.
        """
        return AstraQueryResult(
            documents=[
                [f"text: {result['text']}", f"source: {result['source']}"]
                for result in api_response
            ]
        )
