"""Classes for using tools with Chat APIs."""
import re
from typing import cast

from openai.types.chat import ChatCompletionToolParam
from pydantic import BaseModel


class OpenAITool(BaseModel):
    """A base class for more easily using tools with the OpenAI Chat client."""

    @classmethod
    def tool_schema(cls) -> ChatCompletionToolParam:
        """Constructs a tool schema for use with the OpenAI Chat client.

        Returns:
            The constructed `ChatCompletionToolParam` schema.

        Raises:
            ValueError: if the class doesn't have
        """
        model_schema = cls.model_json_schema()
        if "description" not in model_schema:
            raise ValueError("Tool must have a dosctring description.")

        fn = {
            "name": re.sub(r"(?<!^)(?=[A-Z])", "_", model_schema["title"]).lower(),
            "description": model_schema["description"],
        }
        if model_schema["properties"]:
            fn["parameters"] = {
                "type": "object",
                "properties": {
                    prop: {
                        key: value
                        for key, value in prop_schema.items()
                        if key != "default" and key != "title"
                    }
                    for prop, prop_schema in model_schema["properties"].items()
                },
                "required": model_schema["required"],
            }

        return cast(ChatCompletionToolParam, {"type": "function", "function": fn})
