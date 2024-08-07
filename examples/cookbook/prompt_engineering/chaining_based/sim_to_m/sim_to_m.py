from mirascope.core import openai
from mirascope.core.base.prompt import prompt_template


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    The following is a sequence of events:
    {story}
    What events does {name} know about?
    """
)
def get_one_perspective(story: str, name: str):
    """Gets one person's perspective of a story."""


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    {story_from_perspective}
    Based on the above information, answer the following question:
    {query}
    """
)
def sim_to_m(story: str, query: str, name: str) -> openai.OpenAIDynamicConfig:
    """Executes the flow of the Sim to M technique."""
    story_from_perspective = get_one_perspective(story=story, name=name)
    # Uncomment to see intermediate responses
    # print(story_from_perspective)
    return {"computed_fields": {"story_from_perspective": story_from_perspective}}


story = """Jim put the ball in the box. While Jim wasn't looking, Avi moved the
ball to the basket."""
query = "Where does Jim think the ball is?"

print(sim_to_m(story=story, query=query, name="Jim"))
# > Based on the information provided, Jim thinks the ball is in the box, as he is only aware of his action of putting the ball there and does not know that Avi moved it to the basket.


# Intermediate Responses

# story_from_perspective = get_one_perspective(story=story, name=name)
# > Jim knows about the event of putting the ball in the box. However, he is unaware of Avi moving the ball to the basket because he wasn't looking at that moment. Therefore, Jim only knows about the first event: him putting the ball in the box.
