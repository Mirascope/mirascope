from mirascope.core import vertex, prompt_template
from mirascope.tools import DuckDuckGoSearch


@vertex.call("gemini-1.5-flash", tools=[DuckDuckGoSearch])
@prompt_template("Recommend a {genre} book and summarize the story")
def research(genre: str): ...


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
