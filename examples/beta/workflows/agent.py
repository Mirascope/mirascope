from __future__ import annotations

import logging

from mirascope.beta.workflows import BaseContext, NextStep, step, Workflow
from mirascope.core import openai, BaseDynamicConfig, BaseMessageParam

logging.getLogger().setLevel(logging.DEBUG)


class Context(BaseContext):
    history: list[openai.OpenAIMessageParam]


@step()
def ask_for_help(question: str) -> str:
    """Asks for help from an expert."""
    print("[Assistant Needs Help]")
    print(f"[QUESTION]: {question}")
    answer = input("[ANSWER]: ")
    print("[End Help]")
    return answer


@openai.call("gpt-4o-mini")
def call(query: str, context: Context) -> BaseDynamicConfig:
    messages = [
        BaseMessageParam(role="system", content="You are a librarian"),
        *context["history"],
        BaseMessageParam(role="user", content=query),
    ]
    return {"messages": messages, "tools": [ask_for_help]}


@step()
def query_step(query: str, context: Context) -> NextStep[call_tools]:
    if query:
        context["history"].append(BaseMessageParam(role="user", content=query))
    response = call(query, context)
    return NextStep(call_tools, response)


@step()
def call_tools(
    response: openai.OpenAICallResponse, context: Context
) -> NextStep[run] | NextStep[query_step]:
    context["history"].append(response.message_param)
    tools_and_outputs = []
    if tools := response.tools:
        for tool in tools:
            tools_and_outputs.append((tool, tool.call()))
        context["history"] += response.tool_message_params(tools_and_outputs)
        return NextStep(query_step, "")
    else:
        print("(Assistant): ", end="", flush=True)
        print(response.content)
        return NextStep(run)


@step()
def run(context: Context) -> NextStep[query_step] | None:
    if not context:
        context["history"] = []
    query = input("(User): ")
    if query in ["exit", "quit"]:
        return None
    return NextStep(query_step, query)


wf = Workflow(start=run, stop=run)
result = wf.run()
