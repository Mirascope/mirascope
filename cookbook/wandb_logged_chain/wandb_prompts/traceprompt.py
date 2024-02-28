"""Parent class for prompts that inherit WandB prompt logging functionality."""
from typing import Literal, Union

from pydantic import BaseModel
from utils import get_time_in_ms

from mirascope import OpenAICallParams, Prompt
from mirascope.chat import OpenAIChatCompletion
from wandb.sdk.data_types.trace_tree import Trace


class TracePrompt(Prompt):
    """Parent class for inherited WandB functionality."""

    span_type: Literal["tool", "llm"]
    _call_params: OpenAICallParams = OpenAICallParams(model="gpt-3.5-turbo-1106")

    def span(
        self,
        completion: Union[OpenAIChatCompletion, BaseModel],
        parent: Trace,
        start_time: int,
    ) -> Trace:
        """Returns a span connected to parent."""
        if isinstance(completion, OpenAIChatCompletion):
            if completion.tool and completion.tool.fn:
                output = {
                    "assistant": completion.tool,
                    "tool_output": completion.tool.fn(
                        **completion.tool.model_dump(exclude={"tool_call"})
                    ),
                }
            else:
                output = {"assistant": str(completion)}
        elif isinstance(completion, BaseModel):
            output = {"assistant": str(completion.model_dump())}

        span = Trace(
            name=self.__class__.__name__,
            kind=self.span_type,
            status_code="success",
            status_message=None,
            start_time_ms=start_time,
            end_time_ms=get_time_in_ms(),
            inputs={message["role"]: message["content"] for message in self.messages},
            outputs=output,
        )
        parent.add_child(span)
        return span
