# Query Plan

This recipe shows how to use LLMs — in this case, Anthropic’s Claude 3.5 Sonnet — to create a query plan. Using a query plan is a great way to get more accurate results by breaking down a complex question into multiple smaller questions.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/tools/">Tools</a></li>
<li><a href="../../../learn/chaining/">Chaining</a></li>
<li><a href="../../../learn/json_mode/">JSON Mode</a></li>
<li><a href="../../../learn/response_models/">Response Models</a></li>
</ul>
</div>

## Setup

Let's start by installing Mirascope and its dependencies:


```python
!pip install "mirascope[anthropic]"
```


```python
import os

os.environ["ANTHROPIC_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Create your Query

To construct our Query Plan, we first need to define the individual queries that will comprise it using a Pydantic BaseModel:


```python
from pydantic import BaseModel, Field


class Query(BaseModel):
    id: int = Field(..., description="ID of the query, this is auto-incremented")
    question: str = Field(
        ...,
        description="The broken down question to be answered to answer the main question",
    )
    dependencies: list[int] = Field(
        description="List of sub questions that need to be answered before asking this question",
    )
    tools: list[str] = Field(
        description="List of tools that should be used to answer the question"
    )
```


Each query is assigned a unique ID, which can reference other queries for dependencies. We also provide necessary tools and the relevant portion of the broken-down question to each query.

## Create our tool

For the purposes of this recipe, we will define some dummy data. This tool should be replaced by web_search, a database query, or other forms of pulling data.



```python
import json


def get_weather_by_year(year: int):
    """Made up data to get Tokyo weather by year"""
    if year == 2020:
        data = {
            "jan": 42,
            "feb": 43,
            "mar": 49,
            "apr": 58,
            "may": 66,
            "jun": 72,
            "jul": 78,
            "aug": 81,
            "sep": 75,
            "oct": 65,
            "nov": 55,
            "dec": 47,
        }
    elif year == 2021:
        data = {
            "jan": 45,
            "feb": 48,
            "mar": 52,
            "apr": 60,
            "may": 68,
            "jun": 74,
            "jul": 80,
            "aug": 83,
            "sep": 77,
            "oct": 67,
            "nov": 57,
            "dec": 49,
        }
    else:
        data = {
            "jan": 48,
            "feb": 52,
            "mar": 56,
            "apr": 64,
            "may": 72,
            "jun": 78,
            "jul": 84,
            "aug": 87,
            "sep": 81,
            "oct": 71,
            "nov": 61,
            "dec": 53,
        }
    return json.dumps(data)
```


## Define our Query Planner

Let us prompt our LLM call to create a query plan for a particular question:



```python
from mirascope.core import anthropic, prompt_template


@anthropic.call(
    model="claude-3-5-sonnet-20240620", response_model=list[Query], json_mode=True
)
@prompt_template(
    """
    SYSTEM:
    You are an expert at creating a query plan for a question.
    You are given a question and you need to create a query plan for it.
    You need to create a list of queries that can be used to answer the question.

    You have access to the following tool:
    - get_weather_by_year
    USER:
    {question}
    """
)
def create_query_plan(question: str): ...
```


We set the `response_model` to the `Query` object we just defined. We also prompt the call to add tools as necessary to the individual `Query`. Now we make a call to the LLM:



```python
query_plan = create_query_plan("Compare the weather in Tokyo from 2020 to 2022")
print(query_plan)
```

    [Query(id=1, question='What was the weather like in Tokyo in 2020?', dependencies=[], tools=['get_weather_by_year']), Query(id=2, question='What was the weather like in Tokyo in 2021?', dependencies=[], tools=['get_weather_by_year']), Query(id=3, question='What was the weather like in Tokyo in 2022?', dependencies=[], tools=['get_weather_by_year']), Query(id=4, question='Compare the weather data for Tokyo from 2020 to 2022', dependencies=[1, 2, 3], tools=[])]



We can see our `list[Query]` and their respective subquestions and tools needed to answer the main question. We can also see that the final question depends on the answers from the previous queries.

## Executing our Query Plan

Now that we have our list of queries, we can iterate on each of the subqueries to answer our main question:



```python
from anthropic.types import MessageParam


@anthropic.call(model="claude-3-5-sonnet-20240620")
@prompt_template(
    """
    MESSAGES:
    {history}
    USER:
    {question}
    """
)
def run(
    question: str, history: list[MessageParam], tools: list[str]
) -> anthropic.AnthropicDynamicConfig:
    tools_fn = [eval(tool) for tool in tools]
    return {"tools": tools_fn}


def execute_query_plan(query_plan: list[Query]):
    results = {}
    for query in query_plan:
        history = []
        for dependency in query.dependencies:
            result = results[dependency]
            history.append({"role": "user", "content": result["question"]})
            history.append({"role": "assistant", "content": result["content"]})
        result = run(query.question, history, query.tools)
        if tool := result.tool:
            output = tool.call()
            results[query.id] = {"question": query.question, "content": output}
        else:
            return result.content
    return results
```


Using Mirascope’s `DynamicConfig` , we can pass in the tools from the query plan into our LLM call. We also add history to the calls that have dependencies.

Now we run `execute_query_plan`:



```python
result = execute_query_plan(query_plan)
print(result)
```

    Comparing the weather data for Tokyo from 2020 to 2022, we can observe the following trends:
    
    1. Overall warming trend:
       - There's a consistent increase in temperatures across all months from 2020 to 2022.
       - The average annual temperature has risen each year.
    
    2. Monthly comparisons:
       - January: 42°F (2020) → 45°F (2021) → 48°F (2022)
       - July: 78°F (2020) → 80°F (2021) → 84°F (2022)
       - December: 47°F (2020) → 49°F (2021) → 53°F (2022)
    
    3. Seasonal patterns:
       - Winters (Dec-Feb) have become milder each year.
       - Summers (Jun-Aug) have become hotter each year.
       - Spring and autumn months also show warming trends.
    
    4. Extreme temperatures:
       - The hottest month has consistently been August, with temperatures increasing from 81°F (2020) to 87°F (2022).
       - The coldest month has consistently been January, with temperatures rising from 42°F (2020) to 48°F (2022).
    
    5. Year-to-year changes:
       - The temperature increase from 2020 to 2021 was generally smaller than the increase from 2021 to 2022.
       - 2022 shows the most significant warming compared to previous years.
    
    In summary, the data indicates a clear warming trend in Tokyo from 2020 to 2022, with each year being warmer than the last across all seasons.


<div class="admonition tip">
<p class="admonition-title">Additional Real-World Examples</p>
<ul>
<li><b>Enhanced ChatBot</b>: Provide higher quality and more accurate answers by using a query plan to answer complex questions.</li>
<li><b>Database Administrator</b>: Translate layperson requests into a query plan, then execute SQL commands to efficiently retrieve or manipulate data, fulfilling the user's requirements.</li>
<li><b>Customer support</b>: Take a user request and turn it into a query plan for easy to follow and simple instructions for troubleshooting.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider the following:

    - Agentic: Turn this example into a more flexible Agent which has access to a query plan tool.
    - Multiple providers: Use multiple LLM providers to verify whether the extracted information is accurate and not hallucination.
    - Implement Pydantic `ValidationError` and Tenacity `retry` to improve reliability and accuracy.

