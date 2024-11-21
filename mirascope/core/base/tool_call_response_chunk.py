from pydantic import BaseModel


class ToolCallNameResponseChunk(BaseModel):
    """
    A chunk that contains the name and ID of a streamed tool call.
    """

    name: str
    id: str


class ToolCallArgumentsResponseChunk(BaseModel):
    """
    A chunk that contains a delta in the function arguments of a streamed tool call.
    """

    delta: str
