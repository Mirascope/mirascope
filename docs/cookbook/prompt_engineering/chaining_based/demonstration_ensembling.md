# Demonstration Ensembling: Enhancing LLM Responses with Aggregated Examples

Demonstration Ensembling is a prompt engineering technique which comprises of taking an aggregate of multiple responses, each of which have been trained on a random subset of examples from the example pool. This recipe demonstrates how to implement Demonstration Ensembling using Large Language Models (LLMs) with Mirascope.

??? tip "Mirascope Concepts Used"

    - [Prompts](../../learn/prompts.md)
    - [Calls](../../learn/calls.md)
    - [Dynamic Configuration](../../learn/dynamic_configuration.md)

!!! note "Background"

    [Demonstration Ensembling](https://arxiv.org/pdf/2308.08780) is a technique that aims to improve the quality and consistency of LLM responses by leveraging multiple examples and aggregating results. It's particularly useful when dealing with tasks that benefit from diverse perspectives or when you want to reduce the impact of potential biases in individual examples.

## Implementation

Let's implement the Demonstration Ensembling technique using Mirascope:

```python
import asyncio
import random

from mirascope.core import openai, prompt_template

qa_examples = [
    "Q: What are your company's core values?\nA: Our company's core values are integrity, innovation, customer-centricity, and teamwork. We believe that maintaining these values is crucial to achieving our mission and vision.",
    "Q: How do you handle conflicts in the workplace?\nA: We handle conflicts by promoting open communication, understanding different perspectives, and seeking mutually beneficial solutions. We have clear policies and trained mediators to assist in resolving conflicts effectively.",
    "Q: Can you describe a time when you exceeded a client's expectations?\nA: Certainly. Recently, we completed a project ahead of schedule and under budget. We also provided additional insights and recommendations that significantly benefited the client, earning their gratitude and loyalty.",
    "Q: How do you ensure continuous improvement within the team?\nA: We ensure continuous improvement by encouraging regular training, fostering a culture of feedback, and implementing agile methodologies. We also review our processes regularly to identify areas for enhancement.",
    "Q: What strategies do you use to stay ahead of industry trends?\nA: We stay ahead of industry trends by investing in research and development, attending industry conferences, and maintaining strong relationships with thought leaders. We also encourage our team to engage in continuous learning and innovation.",
    "Q: How do you measure the success of a project?\nA: We measure the success of a project by evaluating key performance indicators such as client satisfaction, budget adherence, timeline compliance, and the quality of the deliverables. Post-project reviews help us to identify successes and areas for improvement.",
    "Q: What is your approach to diversity and inclusion?\nA: Our approach to diversity and inclusion involves creating a welcoming environment for all employees, offering diversity training, and implementing policies that promote equality. We value diverse perspectives as they drive innovation and growth.",
    "Q: How do you manage remote teams effectively?\nA: We manage remote teams effectively by leveraging technology for communication and collaboration, setting clear goals, and maintaining regular check-ins. We also ensure that remote employees feel included and supported.",
    "Q: What are your short-term and long-term goals for the company?\nA: In the short term, our goals include expanding our market reach and enhancing our product offerings. In the long term, we aim to become industry leaders by driving innovation and achieving sustainable growth.",
    "Q: How do you handle feedback from clients or customers?\nA: We handle feedback by listening actively, responding promptly, and taking necessary actions to address concerns. We view feedback as an opportunity for improvement and strive to exceed our clients' expectations continuously.",
]

@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Here are some examples that demonstrate the voice to use in a corporate setting.
    {examples:list}

    With these examples, answer the following question:
    {query}
    """
)
async def answer(query: str) -> openai.OpenAIDynamicConfig:
    random_indices = random.sample(range(len(qa_examples)), 3)
    examples = [
        f"Question: {qa_examples[i]['question']}\nAnswer: {qa_examples[i]['answer']}"
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
    return {
        "computed_fields": {"responses": responses}
    }

async def demonstration_ensembling(query, ensemble_size):
    response = await aggregate_answers(query=query, num_responses=ensemble_size)
    print(response.content)

query = """Help me write a notice that highlights the importance of attending \
the company's social events. Give me just the notice, no further explanation."""

asyncio.run(demonstration_ensembling(query=query, ensemble_size=5))
# > **Notice: Importance of Attending Company Social Events**
# 
#   Dear Team,
#   
#   We want to highlight the significance of participating in our upcoming company social events. These gatherings are valuable opportunities for team bonding, networking, and fostering a positive workplace culture. Engaging with colleagues outside of our regular work environment enhances collaboration, strengthens relationships, and supports a cohesive team atmosphere.
#   
#   Your presence at these events not only enriches the experience for yourself but also contributes greatly to our vibrant community. We encourage everyone to attend, connect with one another, and celebrate our successes together.
#   
#   Thank you for your commitment to making our workplace a supportive and dynamic environment.
#   
#   Best regards,
#   [Your Name]
#   [Your Position]
```

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

!!! tip "Additional Real-World Applications"

    - Content Generation: Use Demonstration Ensembling to create more diverse and comprehensive marketing materials.
    - Customer Support: Generate more robust and consistent responses to customer inquiries.
    - Data Analysis: Produce more reliable insights by aggregating multiple interpretations of data.
    - Educational Content: Create well-rounded explanations of complex topics by combining multiple teaching approaches.

When adapting this recipe to your specific use-case, consider:

- Tailoring the example pool to your domain for better performance.
- Implementing different methods of selecting examples (e.g., weighted sampling based on relevance).
- Combining Demonstration Ensembling with other techniques like Chain of Thought for even more nuanced responses.
- Developing a feedback mechanism to continuously improve the quality of the example pool.

By leveraging Mirascope's `call` decorator, response models, and dynamic configuration, you can easily implement and customize the Demonstration Ensembling technique to enhance your LLM's response quality across a wide range of applications.
