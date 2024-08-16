from typing import Literal

from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template


class User(BaseModel):
    name: str
    email: str
    past_purchases: list[str]
    past_charges: list[float]
    payment_method: str
    password: str
    security_question: str
    security_answer: str


def get_user_by_email(email: str):
    if email == "johndoe@gmail.com":
        return User(
            name="John Doe",
            email="johndoe@gmail.com",
            past_purchases=["TV", "Microwave", "Chair"],
            past_charges=[349.99, 349.99, 99.99, 44.99],
            payment_method="AMEX 1234 1234 1234 1234",
            password="password1!",
            security_question="Childhood Pet Name",
            security_answer="Piddles",
        )
    else:
        return None


def get_sale_items():
    return "Sale items: we have a monitor at half off for $80!"


def get_rewards(user: User):
    if sum(user.past_charges) > 300:
        return "Rewards: for your loyalty, you get 10% off your next purchase!"
    else:
        return "Rewards: you have no rewards available right now."


def get_billing_details(user: User):
    return {
        "user_email": user.email,
        "user_name": user.name,
        "past_purchases": user.past_purchases,
        "past_charges": user.past_charges,
    }


def get_account_details(user: User):
    return {
        "user_email": user.email,
        "user_name": user.name,
        "password": user.password,
        "security_question": user.security_question,
        "security_answer": user.security_answer,
    }


def route_to_agent(
    agent_type: Literal["billing", "sale", "support"], summary: str
) -> None:
    """Routes the call to an appropriate agent with a summary of the issue."""
    print(f"Routed to: {agent_type}\nSummary:\n{summary}")


class CallClassification(BaseModel):
    calltype: Literal["billing", "sale", "support"] = Field(
        ...,
        description="""The classification of the customer's issue into one of the 3: 
        'billing' for an inquiry about charges or payment methods,
        'sale' for making a purchase,
        'support' for general FAQ or account-related questions""",
    )
    reasoning: str = Field(
        ...,
        description="""A brief description of why the customer's issue fits into the\
              chosen category""",
    )
    user_email: str = Field(..., description="email of the user in the chat")


@openai.call(model="gpt-4o-mini", response_model=CallClassification)
@prompt_template(
    """
    Classify the following transcript between a customer and the service bot:
    {transcript}
    """
)
def classify_transcript(transcript: str): ...


@openai.call(model="gpt-4o-mini", tools=[route_to_agent])
@prompt_template(
    """
    SYSTEM:
    You are an intermediary between a customer's interaction with a support chatbot and
    a real life support agent. Organize the context so that the agent can best
    facilitate the customer, but leave in details or raw data that the agent would need
    to verify a person's identity or purchase. Then, route to the appropriate agent.

    USER:
    {context}
    """
)
def handle_ticket(transcript: str) -> openai.OpenAIDynamicConfig:
    context = transcript
    call_classification = classify_transcript(transcript)
    user = get_user_by_email(call_classification.user_email)
    if isinstance(user, User):
        if call_classification.calltype == "billing":
            context += str(get_billing_details(user))
        elif call_classification.calltype == "sale":
            context += get_sale_items()
            context += get_rewards(user)
        elif call_classification.calltype == "support":
            context += str(get_account_details(user))
    else:
        context = "This person cannot be found in our system."

    return {"computed_fields": {"context": context}}


billing_transcript = """
BOT: Please enter your email.
CUSTOMER: johndoe@gmail.com
BOT: What brings you here today?
CUSTOMER: I purchased a TV a week ago but the charge is showing up twice on my bank \
statement. Can I get a refund?
"""

sale_transcript = """
BOT: Please enter your email.
CUSTOMER: johndoe@gmail.com
BOT: What brings you here today?
CUSTOMER: I'm looking to buy a new monitor. Any discounts available?
"""

support_transcript = """
BOT: Please enter your email.
CUSTOMER: johndoe@gmail.com
BOT: What brings you here today?
CUSTOMER: I forgot my site password and I'm also locked out of my email, how else can I
verify my identity?
"""

for transcript in [billing_transcript, sale_transcript, support_transcript]:
    response = handle_ticket(transcript)
    if tool := response.tool:
        tool.call()
