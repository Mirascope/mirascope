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
    {examples}

    With these examples, answer the following question:
    {query}
    """
)
async def answer(query: str) -> openai.OpenAIDynamicConfig:
    random_indices = random.sample(range(len(qa_examples)), 3)
    examples = [qa_examples[i] for i in random_indices]
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
    # Uncomment to see intermediate responses
    print([response.content for response in responses])

    return {
        "computed_fields": {"responses": [response.content for response in responses]}
    }


query = """Help me write a notice that highlights the importance of attending\
the company's social events. Give me just the notice, no further explanation."""


async def demonstration_ensembling(query, ensemble_size):
    print(await aggregate_answers(query=query, num_responses=ensemble_size))


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


# Intermediate Responses

# print([response.content for response in responses])
# NOTICE: Importance of Attending Company Social Events

# Dear Team,

# We are excited to remind everyone about the significance of participating in our upcoming social events. These gatherings provide a unique opportunity to foster connections, strengthen team dynamics, and enhance our company culture. Engaging in social activities allows us to build relationships outside of our typical work environment, promoting collaboration and teamwork.

# Your presence is vital in creating a vibrant and inclusive atmosphere where everyone feels valued and connected. Let’s come together to celebrate our successes and continue to build a strong community within our organization.

# We look forward to seeing you all there!

# Best Regards,
# [Your Name]
# [Your Position]

# Notice: Importance of Attending Company Social Events

# Dear Team,

# We would like to emphasize the significance of participating in our company social events. These gatherings provide valuable opportunities for team building, strengthening relationships, and fostering a positive workplace culture. Engaging with colleagues outside of our regular work routine enhances collaboration and communication, ultimately contributing to our shared success.

# We encourage everyone to make an effort to attend these events. Your participation not only enriches the experience for yourself but also supports a cohesive and motivated team environment.

# Thank you for your commitment to making our workplace a vibrant community.

# Best regards,
# [Your Company Name]

# Notice: Importance of Attending Company Social Events

# Dear Team,

# We would like to emphasize the importance of participating in our upcoming company social events. These gatherings provide a valuable opportunity for team bonding, networking, and fostering a positive workplace culture. Engaging with your colleagues outside of the usual work environment helps strengthen relationships, promotes collaboration, and enhances overall team spirit.

# We encourage everyone to attend and make the most of these events. Your presence not only enriches the experience but also contributes to the vibrant culture we strive to create at our company.

# Thank you for your participation and enthusiasm!

# Best regards,
# [Your Name]
# [Your Position]

# Notice: Importance of Attending Company Social Events

# Dear Team,

# We would like to emphasize the significance of participating in our upcoming social events. These gatherings provide an excellent opportunity for team building, fostering relationships, and enhancing our corporate culture. Connecting with colleagues outside of the traditional work environment allows for stronger collaboration and communication across departments.

# Your presence not only contributes to a positive workplace atmosphere but also helps in cultivating a sense of community within our organization. We encourage everyone to engage, share ideas, and connect with one another during these events.

# Thank you for your participation!

# Best regards,
# [Your Name]
# [Your Position]

# Notice: Importance of Attending Company Social Events

# Dear Team,

# We would like to take a moment to emphasize the significance of participating in our upcoming company social events. These gatherings are not only an opportunity to unwind and enjoy each other's company, but they also play a crucial role in fostering teamwork, collaboration, and a sense of community within our organization.

# Attending these events allows you to connect with colleagues from different departments, share experiences, and build relationships that enhance our workplace culture. It is through these interactions that we can strengthen our bonds and create a more cohesive and productive environment.

# We encourage everyone to make time for these events, as your participation is vital to the success of our team dynamics and overall morale. Let’s come together to celebrate our achievements, support one another, and continue to promote a positive workplace atmosphere.

# Thank you for your commitment to making our company a great place to work.

# Best regards,
# [Your Name]
# [Your Title]
