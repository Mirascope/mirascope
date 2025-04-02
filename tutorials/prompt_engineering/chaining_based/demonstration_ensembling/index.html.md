# Demonstration Ensembling: Enhancing LLM Responses with Aggregated Examples

Demonstration Ensembling is a prompt engineering technique which comprises of taking an aggregate of multiple responses, each of which have been trained on a random subset of examples from the example pool. This recipe demonstrates how to implement Demonstration Ensembling using Large Language Models (LLMs) with Mirascope.

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Code Generation</b>: Break down complex programming tasks into smaller, manageable steps.</li>
<li><b>Data Analysis</b>: Decompose complex data analysis queries into a series of data manipulation and calculation steps.</li>
<li><b>Natural Language Processing</b>: Break down complex NLP tasks like sentiment analysis or named entity recognition into subtasks.</li>
<li><b>Automated Reasoning</b>: Solve complex logical or mathematical problems by breaking them into simpler, solvable steps.</li>
<li><b>Task Planning</b>: Create detailed, step-by-step plans for complex projects or processes.</li>
</ul>
</div>

## Implementation

Let's implement the Demonstration Ensembling technique using Mirascope:



```python
import asyncio
import random
from typing import TypedDict

from mirascope.core import openai, prompt_template


class QA(TypedDict):
    question: str
    answer: str


qa_examples: list[QA] = [
    QA(
        question="What are your company's core values?",
        answer="Our company's core values are integrity, innovation, customer-centricity, and teamwork. We believe that maintaining these values is crucial to achieving our mission and vision.",
    ),
    QA(
        question="How do you handle conflicts in the workplace?",
        answer="We handle conflicts by promoting open communication, understanding different perspectives, and seeking mutually beneficial solutions. We have clear policies and trained mediators to assist in resolving conflicts effectively.",
    ),
    QA(
        question="Can you describe a time when you exceeded a client's expectations?",
        answer="Certainly. Recently, we completed a project ahead of schedule and under budget. We also provided additional insights and recommendations that significantly benefited the client, earning their gratitude and loyalty.",
    ),
    QA(
        question="How do you ensure continuous improvement within the team?",
        answer="We ensure continuous improvement by encouraging regular training, fostering a culture of feedback, and implementing agile methodologies. We also review our processes regularly to identify areas for enhancement.",
    ),
    QA(
        question="What strategies do you use to stay ahead of industry trends?",
        answer="We stay ahead of industry trends by investing in research and development, attending industry conferences, and maintaining strong relationships with thought leaders. We also encourage our team to engage in continuous learning and innovation.",
    ),
    QA(
        question="How do you measure the success of a project?",
        answer="We measure the success of a project by evaluating key performance indicators such as client satisfaction, budget adherence, timeline compliance, and the quality of the deliverables. Post-project reviews help us to identify successes and areas for improvement.",
    ),
    QA(
        question="What is your approach to diversity and inclusion?",
        answer="Our approach to diversity and inclusion involves creating a welcoming environment for all employees, offering diversity training, and implementing policies that promote equality. We value diverse perspectives as they drive innovation and growth.",
    ),
    QA(
        question="How do you manage remote teams effectively?",
        answer="We manage remote teams effectively by leveraging technology for communication and collaboration, setting clear goals, and maintaining regular check-ins. We also ensure that remote employees feel included and supported.",
    ),
    QA(
        question="What are your short-term and long-term goals for the company?",
        answer="In the short term, our goals include expanding our market reach and enhancing our product offerings. In the long term, we aim to become industry leaders by driving innovation and achieving sustainable growth.",
    ),
    QA(
        question="How do you handle feedback from clients or customers?",
        answer="We handle feedback by listening actively, responding promptly, and taking necessary actions to address concerns. We view feedback as an opportunity for improvement and strive to exceed our clients' expectations continuously.",
    ),
]


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Here are some examples that demonstrate the voice to use in a corporate setting.
    {examples:lists}

    With these examples, answer the following question:
    {query}
    """
)
async def answer(query: str) -> openai.OpenAIDynamicConfig:
    random_indices = random.sample(range(len(qa_examples)), 3)
    examples = [
        [
            f"Question: {qa_examples[i]['question']}",
            f"Answer: {qa_examples[i]['answer']}",
        ]
        for i in random_indices
    ]
    return {"computed_fields": {"examples": examples}}


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Take the following responses from an LLM and aggregate/average them into
    one answer.
    {responses}
    """
)
async def aggregate_answers(
    query: str, num_responses: int
) -> openai.OpenAIDynamicConfig:
    tasks = [answer(query) for _ in range(num_responses)]
    responses = await asyncio.gather(*tasks)
    return {"computed_fields": {"responses": responses}}


async def demonstration_ensembling(query, ensemble_size):
    response = await aggregate_answers(query=query, num_responses=ensemble_size)
    print(response.content)


query = """Help me write a notice that highlights the importance of attending \
the company's social events. Give me just the notice, no further explanation."""

await demonstration_ensembling(query=query, ensemble_size=5)
```

    Here is an aggregated notice highlighting the importance of attending the company's social events:
    
    ---
    
    **Notice: Importance of Attending Company Social Events**
    
    Dear Team,
    
    We would like to emphasize the significance of participating in our upcoming company social events. These gatherings provide a valuable opportunity to connect with colleagues, foster teamwork, and build a positive workplace culture. Engaging in social activities enhances collaboration and strengthens relationships across departments.
    
    We encourage everyone to attend and contribute to our vibrant community. Your presence is vital to making these events successful and enjoyable for all, and it enriches both your experience and that of your coworkers.
    
    Thank you for your continued commitment to making our workplace more connected and enjoyable.
    
    Best regards,  
    [Your Name]  
    [Your Position]  
    
    --- 
    
    This notice combines essential elements from all responses to create a cohesive message.


This implementation consists of three main functions:

1. `answer`: This function takes a query and returns a response based on a random subset of examples.
2. `aggregate_answers`: This function generates multiple responses using `answer` and then aggregates them.
3. `demonstration_ensembling`: This function orchestrates the entire process, calling `aggregate_answers` with the specified ensemble size.

## Benefits and Considerations

The Demonstration Ensembling technique offers several advantages:

1. Improved consistency and quality of responses by leveraging multiple examples.
2. Reduced impact of potential biases in individual examples.
3. Enhanced ability to generate responses that capture diverse perspectives.

When implementing this technique, consider:

- Balancing the ensemble size with computational cost and time constraints.
- Carefully curating the example pool to ensure diversity and relevance.
- Experimenting with different aggregation methods for the final response.

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Content Generation</b>: Use Demonstration Ensembling to create more diverse and comprehensive marketing materials.</li>
<li><b>Customer Support</b>: Generate more robust and consistent responses to customer inquiries.</li>
<li><b>Data Analysis</b>: Produce more reliable insights by aggregating multiple interpretations of data.</li>
<li><b>Educational Content</b>: Create well-rounded explanations of complex topics by combining multiple teaching approaches.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider:

- Tailoring the example pool to your domain for better performance.
- Implementing different methods of selecting examples (e.g., weighted sampling based on relevance).
- Combining Demonstration Ensembling with other techniques like Chain of Thought for even more nuanced responses.
- Developing a feedback mechanism to continuously improve the quality of the example pool.

