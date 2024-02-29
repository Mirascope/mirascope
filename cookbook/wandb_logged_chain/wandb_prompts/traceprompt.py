"""Parent class for prompts that inherit WandB prompt logging functionality."""
from typing import Literal, Union

from pydantic import BaseModel
from wandb.sdk.data_types.trace_tree import Trace

from mirascope import OpenAICallParams, Prompt
from mirascope.chat import OpenAIChatCompletion


class TracePrompt(Prompt):
    """Parent class for inherited WandB functionality."""

    span_type: Literal["tool", "llm"]
    call_params: OpenAICallParams = OpenAICallParams(model="gpt-3.5-turbo-0125")

    def span(
        self, completion: Union[OpenAIChatCompletion, BaseModel], parent: Trace
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
            dump = completion.dump()
        elif isinstance(completion, BaseModel):
            output = {"assistant": str(completion.model_dump())}
            dump = completion._completion.dump()  # type: ignore

        span = Trace(
            name=self.__class__.__name__,
            kind=self.span_type,
            status_code="success",
            status_message=None,
            start_time_ms=dump["start_time"],
            end_time_ms=dump["end_time"],
            inputs={message["role"]: message["content"] for message in self.messages},
            outputs=output,
        )
        parent.add_child(span)
        return span
