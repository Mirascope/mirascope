from mirascope.core import groq, prompt_template
from mirascope.tools import DuckDuckGoSearch


@groq.call("llama-3.1-70b-versatile", tools=[DuckDuckGoSearch])
@prompt_template("Recommend a {genre} book and summarize the story")
def research(genre: str): ...


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
