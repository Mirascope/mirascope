import inspect

from mirascope import llm

from .utils import async_tool, prompt, tool


async def combine_tool_outputs():
    call: llm.calls.Call = llm.call(
        model="openai:gpt-4o-mini", tools=[tool, async_tool]
    )(prompt)
    response: llm.Response = call()
    while tool_calls := response.tool_calls:
        outputs: list[llm.ToolOutput] = []
        for tool_call in tool_calls:
            output = call.toolkit.execute(tool_call)
            if inspect.isawaitable(output):
                output = await output
            outputs.append(output)
        response = call.resume(response, outputs)
