from pydantic import BaseModel, ConfigDict


class BaseQueryResults(BaseModel):
    """The results of a query."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)
