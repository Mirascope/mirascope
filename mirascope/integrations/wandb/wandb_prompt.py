"""Prompts with WandB and OpenAI integration to support logging functionality."""
from typing import Literal, Union

from pydantic import BaseModel
from wandb.sdk.data_types.trace_tree import Trace

from mirascope import BaseCallParams, Prompt
from mirascope.chat import OpenAIChatCompletion


class WandbPrompt(Prompt):
    """Parent class for inherited WandB functionality."""

    span_type: Literal["tool", "llm"]

    call_params = BaseCallParams(model="gpt-3.5-turbo-0125")

    def trace(
        self, completion: Union[OpenAIChatCompletion, BaseModel], parent: Trace
    ) -> Trace:
        """Returns a trace connected to parent.

        Args:
            completion: The completion to trace. Handles `OpenAIChatCompletion` output
                from both standard OpenAI chat completions, and `BaseModel` for
                extractions.
            parent: The parent trace to connect to.

        Returns:
            The created trace, connected to the parent.
        """
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
            if not hasattr(completion, "_completion"):
                raise ValueError(
                    "Completion of type `BaseModel` was not created using the `extract`"
                    " function and does not contain the necessary `_completion` private"
                    " attribute."
                )
            else:
                dump = completion._completion.dump()

        span = Trace(
            name=self.__class__.__name__,
            kind=self.span_type,
            status_code="success",
            status_message=None,
            metadata={"model": self.call_params.model},
            start_time_ms=dump["start_time"],
            end_time_ms=dump["end_time"],
            inputs={message["role"]: message["content"] for message in self.messages},
            outputs=output,
        )
        parent.add_child(span)
        return span

    def trace_error(self, error: Exception, parent: Trace) -> Trace:
        """Returns an error trace connected to parent.

        Args:
            error: The error to trace.
            parent: The parent trace to connect to.

        Returns:
            The created error trace, connected to the parent.
        """
        span = Trace(
            name=self.__class__.__name__,
            kind=self.span_type,
            status_code="error",
            status_message=str(error),
            metadata={"model": self.call_params.model},
            start_time_ms=None,
            end_time_ms=None,
            inputs={message["role"]: message["content"] for message in self.messages},
            outputs=None,
        )
        parent.add_child(span)
        return span
