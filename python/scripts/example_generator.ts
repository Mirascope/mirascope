export interface ExampleOptions {
  async: boolean;
  stream: boolean;
  context: boolean;
  tools: boolean;
  agent: boolean;
  structured: boolean;
}

export function allOptions(): ExampleOptions[] {
  const bools = [false, true];
  const results: ExampleOptions[] = [];
  for (const agent of bools) {
    for (const context of bools) {
      for (const structured of bools) {
        for (const tools of bools) {
          for (const stream of bools) {
            for (const async of bools) {
              results.push({
                async,
                stream,
                context,
                tools,
                agent,
                structured,
              });
            }
          }
        }
      }
    }
  }
  return results;
}

export function filenameForOptions(opts: ExampleOptions): string {
  const parts: string[] = ["sazed"];
  if (opts.async) parts.push("async");
  if (opts.stream) parts.push("stream");
  if (opts.tools) parts.push("tools");
  if (opts.agent) parts.push("agent");
  if (opts.context) parts.push("context");
  if (opts.structured) parts.push("structured");
  return `${parts.join("_")}.py`;
}

export class ExampleGenerator implements ExampleOptions {
  async: boolean;
  stream: boolean;
  context: boolean;
  tools: boolean;
  agent: boolean;
  structured: boolean;
  mcp: boolean;

  constructor(private options: ExampleOptions) {
    Object.assign(this, options);
  }

  generate(): string {
    return `${this.imports}${this.format_def}${this.coppermind_def}${this.tool_def}
${this.function_decorator}
${this.function_def}

${this.main_function}${this.invoke_main}
`;
  }

  private get docstring(): string {
    return "Example mirascope usage.";
  }
  private get imports(): string {
    let imports = "";
    if (this.async) {
      imports += "import asyncio\n";
    }
    if (this.context) {
      imports += "from dataclasses import dataclass\n";
    }
    if (this.async || this.context) {
      imports += "\n";
    }

    if (this.structured) {
      imports += "from pydantic import BaseModel\n\n";
    }

    imports += "from mirascope import llm\n\n";
    return imports;
  }

  private get format_def(): string {
    if (!this.structured) return "";
    return `
@llm.format(mode="strict-or-tool")
class KeeperEntry(BaseModel):
    topic: str
    summary: str
    sources: list[str]\n\n`;
  }

  private get coppermind_def(): string {
    if (!this.context) return "";
    return `
@dataclass
class Coppermind:
    repository: str\n\n`;
  }

  private ctx_argdef(trailingComma = false): string {
    const suffix = trailingComma ? ", " : "";
    return this.context ? `ctx: llm.Context[Coppermind]${suffix}` : "";
  }

  private get tool_def(): string {
    if (!this.tools) return "";
    const repository = this.context ? "{ctx.deps.repository}" : "";
    const message = this.context
      ? `You consult ${repository}, and recall the following about {query}...`
      : `You recall the following about {query}...`;
    return `
@llm.${this.context ? "context_" : ""}tool
${this._async}def search_coppermind(${this.ctx_argdef(true)}query: str) -> str:
    """Search your coppermind for information."""
    return f"${message}"\n\n`;
  }

  private get system_prompt(): string {
    const repo_ref = this.context ? "{ctx.deps.repository}" : "ancient";
    return (
      (this.context ? "f" : "") +
      `"""
    You are Sazed, a Keeper from Brandon Sanderson's Mistborn series. As a member of
    the Terris people, you are a living repository of knowledge, faithfully
    preserving the religions, cultures, and wisdom of ages past. You speak with
    the measured cadence of a scholar, often referencing the ${repo_ref} knowledge
    you keep. Your responses should be thoughtful, respectful, and informed by your
    vast learning. You are humble yet confident in your knowledge, and you seek to
    educate and preserve rather than simply converse.
    """`
    );
  }

  private get ctx_arg(): string {
    return this.context ? "ctx, " : "";
  }

  private get ctx_type(): string {
    return this.context ? "Coppermind" : "None";
  }

  private get _await(): string {
    return this.async ? "await " : "";
  }

  private get _async(): string {
    return this.async ? `async ` : "";
  }

  private get stream_type(): string {
    let generic = "";
    let asyncPart = this.async ? "llm.AsyncStream" : "llm.Stream";
    if (this.structured) {
      generic = `[${asyncPart}, KeeperEntry]`;
    } else if (this.async) {
      generic = `[${asyncPart}]`;
    }
    return `llm.StreamResponse${generic}`;
  }

  private get agent_type(): string {
    const base = this.async ? "AsyncAgent" : "Agent";
    let generics = "";
    if (this.structured || this.context) {
      const parts: string[] = [this.ctx_type];
      if (this.structured) parts.push("KeeperEntry");
      generics = `[${parts.join(", ")}]`;
    }
    return `llm.${base}${generics}`;
  }

  private get function_decorator(): string {
    const tools_param = this.tools ? " tools=[search_coppermind]," : "";
    const format_param = this.structured ? " format=KeeperEntry," : "";
    const args =
      tools_param || format_param ? `, ${tools_param}${format_param}` : "";
    const decorator = this.agent
      ? "agent"
      : this.context
      ? "context_call"
      : "call";
    return `@llm.${decorator}(model="openai:gpt-4o-mini"${args})`;
  }

  private get function_def(): string {
    if (this.agent) {
      return `${this._async}def sazed(${this.ctx_argdef()}):
    return ${this.system_prompt}`;
    } else {
      return `${this._async}def sazed(${this.ctx_argdef(true)}query: str):
    system_prompt = ${this.system_prompt}
    return [llm.messages.system(system_prompt), llm.messages.user(query)]`;
    }
  }

  private get main_function(): string {
    let result = `
${this._async}def main():`;

    if (this.context) {
      result += `
    coppermind = Coppermind(repository="Ancient Terris")`;
      if (!this.agent) {
        result += `
    ctx = llm.Context(deps=coppermind)`;
      }
    }

    if (this.agent) {
      const deps_arg = this.context ? "deps=coppermind" : "";
      result += `
    agent: ${this.agent_type} = ${this._await}sazed(${deps_arg})`;
    }

    result += `
    query = "What are the Kandra?"`;

    if (this.stream) {
      result += this.stream_impl;
    } else {
      result += this.response_impl;
    }

    return result;
  }

  private get stream_impl(): string {
    const call_target = this.agent
      ? "agent.stream("
      : "sazed.stream(" + this.ctx_arg;

    let result = `
    response: ${this.stream_type} = ${this._await}${call_target}query)`;

    if (this.tools && !this.agent) {
      result += this.tools_stream;
    } else {
      result += this.print_stream("");
    }

    return result;
  }

  private print_stream(indent: string): string {
    const stream_target = this.structured
      ? `${this._await}response.structured_stream()`
      : `${this._await}response.text_stream()`;
    const stream_print = this.structured
      ? `print("[Partial]: ", chunk, flush=True)`
      : `print(chunk, flush=True, end="")`;
    return `
${indent}    ${this._async}for chunk in ${stream_target}:
${indent}        ${stream_print}`;
  }

  private get tools_stream(): string {
    return `
    while True:${this.print_stream("    ")}
        tool_calls = response.tool_calls
        if not tool_calls:
            break
        ${this.gather_tools}
        response = ${this._await}sazed.resume_stream(${
      this.ctx_arg
    }response, outputs)`;
  }

  private get gather_tools(): string {
    const gather = this.async ? "await asyncio.gather(*" : "";
    const gather_close = this.async ? ")" : "";
    return `outputs: list[llm.ToolOutput] = ${gather}[sazed.toolkit.execute(${this.ctx_arg}tool_call) for tool_call in tool_calls]${gather_close}`;
  }

  private get response_impl(): string {
    const response_type = this.structured
      ? "llm.Response[KeeperEntry]"
      : "llm.Response";
    const call_target = this.agent ? "agent(" : "sazed(" + this.ctx_arg;
    let result = `
    response: ${response_type} = ${this._await}${call_target}query)`;

    if (this.tools && !this.agent) {
      const gather = this.async ? "await asyncio.gather(*" : "";
      const gather_close = this.async ? ")" : "";
      result += `
    while tool_calls := response.tool_calls:
        ${this.gather_tools}
        response = ${this._await}sazed.resume(${this.ctx_arg}response, outputs)`;
    }

    if (this.structured) {
      result += `
    entry: KeeperEntry = response.format()
    print(entry)`;
    } else {
      result += `
    print(response.text)`;
    }

    return result;
  }

  private get invoke_main(): string {
    if (this.async) {
      return `


if __name__ == "__main__":
    asyncio.run(main())`;
    } else {
      return `


main()`;
    }
  }
}
