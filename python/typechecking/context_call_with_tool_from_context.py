"""Simple example that showcases getting a tool from context"""

from mirascope import llm

from .utils import tool, tool_call


@llm.context_call("openai:gpt-4o-mini")
def call(ctx: llm.Context[None, llm.tools.Tool]):
    return "hi"


ctx = llm.Context(tools=[tool])
call(ctx)

# Note: Can also be unknown because the context_call has no explicit tools, so
# ContextToolT is unknown - may be worth revisiting.
retrieved_tool: llm.tools.Tool = call.toolkit.get(ctx, tool_call())
