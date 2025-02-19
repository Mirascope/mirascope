# System to Attention (S2A): Enhancing LLM Focus with Query Filtering

This recipe demonstrates how to implement the System to Attention (S2A) technique using Large Language Models (LLMs) with Mirascope. S2A is a prompt engineering method that enhances an LLM's ability to focus on relevant information by filtering out irrelevant context from the initial query.

<details class="tip">
<summary>Mirascope Concepts Used</summary>
<ul>
<li><a href="../../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../../learn/calls/">Calls</a></li>
<li><a href="../../../../learn/response_models/">Response Models</a></li>
</ul>
</details>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p><a href="https://arxiv.org/pdf/2311.11829">System to Attention</a> (S2A) is a prompt engineering technique whereby the prompt is first filtered to remove all irrelevant information from the query. This approach helps LLMs focus on the most pertinent information, potentially improving the accuracy and relevance of their responses, especially for queries containing extraneous or potentially biasing information.</p>
</div>

## Implementation

Let's implement the S2A technique using Mirascope:


```python
from mirascope.core import openai, prompt_template
from pydantic import BaseModel, Field


class RelevantContext(BaseModel):
    context_text: str = Field(
        description="Context text related to the question (includes all content except unrelated sentences)"
    )
    detailed_question: str = Field(description="Detailed question:")


@openai.call(model="gpt-4o-mini", response_model=RelevantContext)
@prompt_template(
    """
    Given the following text by a user, extract the part that is related and useful, so that using that text alone would be good context for providing an accurate and correct answer to the question portion of the text.
    Please include the actual question or query that the user is asking. 
    Separate this into two categories labeled with ”Context text related to the question (includes all content except unrelated sentences):” and ”Detailed question:”.
    Do not use list.
    Text by User: {query}
    """
)
def remove_irrelevant_info(query: str):
    """Reduces a query down to its relevant context and question"""


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Original user query (possibly biased): {query}
    Unbiased context: {context_text}
    Given the above unbiased context, answer the following: {detailed_question}
    """
)
def s2a(query: str) -> openai.OpenAIDynamicConfig:
    """Executes the flow of the System to Attention technique."""
    relevant_context = remove_irrelevant_info(query=query)
    context_text = relevant_context.context_text
    detailed_question = relevant_context.detailed_question
    return {
        "computed_fields": {
            "context_text": context_text,
            "detailed_question": detailed_question,
        }
    }


# Example usage
query = """Sunnyvale is a city in California. \
Sunnyvale has many parks. Sunnyvale city is \
close to the mountains. Many notable people \
are born in Sunnyvale. \
In which city was San Jose's mayor Sam \
Liccardo born?"""

print(s2a(query=query))
```

    Sam Liccardo, the mayor of San Jose, was born in San Jose, California.


This implementation consists of two main functions:

1. `remove_irrelevant_info`: This function takes the original query and extracts the relevant context and the detailed question. It uses a `RelevantContext` response model to structure the output.

2. `s2a`: This is the main function that orchestrates the S2A technique. It first calls `remove_irrelevant_info` to filter the query, then uses the filtered information to generate a response.

## How It Works

1. **Query Filtering**: The `remove_irrelevant_info` function analyzes the input query and separates it into relevant context and the actual question. This step helps remove any irrelevant or potentially biasing information.

2. **Context Separation**: The filtered information is structured into two parts: the context text and the detailed question. This separation allows for more focused processing in the next step.

3. **Unbiased Response Generation**: The `s2a` function uses the filtered context and question to generate a response. By providing the original query alongside the filtered information, it allows the model to be aware of potential biases while focusing on the relevant information.

## Benefits and Considerations

The S2A technique offers several advantages:

1. Improved focus on relevant information, potentially leading to more accurate responses.
2. Reduction of bias from irrelevant context in the original query.
3. Clear separation of context and question, allowing for more structured reasoning.

When implementing this technique, consider:

- Balancing between removing irrelevant information and retaining important context.
- Adjusting the filtering prompt based on the specific domain or type of queries you're dealing with.
- Monitoring the performance to ensure that important information isn't being filtered out unintentionally.

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Customer Support</b>: Filter out emotional language or irrelevant details from customer queries to focus on the core issue.</li>
<li><b>Legal Document Analysis</b>: Extract relevant facts and questions from lengthy legal documents for more efficient processing.</li>
<li><b>Medical Diagnosis Assistance</b>: Focus on key symptoms and patient history while filtering out irrelevant personal information.</li>
<li><b>Educational Q&A Systems</b>: Improve the relevance of answers by focusing on the core educational content of student questions.</li>
<li><b>Research Query Processing</b>: Enhance literature review processes by focusing on the most relevant aspects of research questions.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider:

- Fine-tuning the filtering process for your specific domain or types of queries.
- Experimenting with different prompt formats for both the filtering and answering stages.
- Implementing a feedback loop to continuously improve the quality of the filtering process.
- Combining S2A with other techniques like Chain of Thought or Self-Consistency for even more robust reasoning capabilities.

By leveraging Mirascope's `call` decorator, response models, and dynamic configuration, you can easily implement and customize the System to Attention technique to enhance your LLM's ability to focus on relevant information and provide more accurate responses across a wide range of applications.
