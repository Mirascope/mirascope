from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseVectorStoreParams(BaseModel):
    """The parameters with which to make a vectorstore."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def kwargs(
        self,
    ) -> dict[str, Any]:
        """Returns all parameters for the index as a keyword arguments dictionary."""
        kwargs = {
            key: value for key, value in self.model_dump().items() if value is not None
        }
        return kwargs
