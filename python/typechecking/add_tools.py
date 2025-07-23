from collections.abc import Awaitable

from mirascope import llm
from mirascope.llm.calls import Call
from mirascope.llm.tools import AsyncTool, Tool


@llm.tool
def sync_tool():
    return "42"


@llm.tool
async def async_tool():
    return 43


@llm.call(model="openai:gpt-4o-mini", tools=[sync_tool])
def call_sync():
    return "hi"


@llm.call(model="openai:gpt-4o-mini", tools=[async_tool])
def call_async():
    return "hi"


def sync_tools_only(x: Call[..., Tool]): ...


def async_tools_only(x: Call[..., AsyncTool]): ...


sync_tools_only(call_sync)
sync_tools_only(call_sync.add_tools([sync_tool]))
sync_tools_only(call_sync.add_tools([async_tool]))  # type: ignore[reportArgumentType]

async_tools_only(call_sync)  # type: ignore[reportArgumentType]
async_tools_only(call_async)
async_tools_only(call_async.add_tools([sync_tool]))  # type: ignore[reportArgumentType]


@llm.agent(model="openai:gpt-4o-mini", tools=[sync_tool])
def agent_sync():
    return "hi"


@llm.agent(model="openai:gpt-4o-mini", tools=[async_tool])
def agent_async():
    return "hi"


a: llm.Agent = agent_sync.add_tools([sync_tool])()
x: llm.Agent = agent_sync.add_tools([async_tool])()  # type: ignore[reportArgumentType]

b: Awaitable[llm.AsyncAgent] = agent_sync.add_tools([async_tool])()
c: Awaitable[llm.AsyncAgent] = agent_async.add_tools([sync_tool, async_tool])()
