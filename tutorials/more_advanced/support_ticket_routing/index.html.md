# Support Ticket Routing

This recipe shows how to take an incoming support ticket/call transcript then use an LLM to summarize the issue and route it to the correct person.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/tools/">Tools</a></li>
<li><a href="../../../learn/chaining/">Chaining</a></li>
<li><a href="../../../learn/response_models/">Response Models</a></li>
</ul>
</div>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p>
Traditional machine learning techniques like text classification were previously used to solve routing. LLMs have enhanced routing by being able to better interpret nuances of inquiries as well as using client history and knowledge of the product to make more informed decisions.
</p>
</div>

## Setup

Let's start by installing Mirascope and its dependencies:


```python
!pip install "mirascope[openai]"
```


```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Imitating a Company's Database/Functionality

<div class="admonition note">
<p class="admonition-title">Fake Data</p>
<p>
For both privacy and functionality purposes, these data types and functions in <em>no way</em> represent how a company's API should actually look like. However, extrapolate on these gross oversimplifications to see how the LLM would interact with the company's API.
</p>
</div>

### User

Let’s create a `User` class to represent a customer as well as the function `get_user_by_email()` to imitate how one might search for the user in the database with some identifying information:


```python
from pydantic import BaseModel, Field


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
```

### Data Pulling Functions

Let’s also define some basic functions that one might expect a company to have for specific situations. `get_sale_items()` gets the items currently on sale, `get_rewards()` gets the rewards currently available to a user, `get_billing_details()` returns user data related to billing, and `get_account_details()` returns user data related to their account.




```python
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
```


### Routing to Agent

Since we don’t have an actual endpoint to route to a live agent, let’s use this function `route_to_agent()` as a placeholder:




```python
from typing import Literal


def route_to_agent(
    agent_type: Literal["billing", "sale", "support"], summary: str
) -> None:
    """Routes the call to an appropriate agent with a summary of the issue."""
    print(f"Routed to: {agent_type}\nSummary:\n{summary}")
```


## Handling the Ticket

To handle the ticket, we will classify the issue of the ticket in one call, then use the classification to gather the corresponding context for a second call.

### Classify the Transcript

Assume we have a basic transcript from the customer’s initial interactions with a support bot where they give some identifying information and their issue. We define a Pydantic `BaseModel` schema to classify the issue as well as grab the identifying information. `calltype` classifies the transcript into one of the three categories `billing`, `sale`, and `support`, and `user_email` will grab their email, assuming that’s what the bot asks for. The `reasoning` field will not be used, but forcing the LLM to give a reasoning for its classification choice aids in extraction accuracy, which can be shaky:




```python
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
```


And we can extract information into this schema with the call `classify_transcript()`:



```python
from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini", response_model=CallClassification)
@prompt_template(
    """
    Classify the following transcript between a customer and the service bot:
    {transcript}
    """
)
def classify_transcript(transcript: str): ...
```

### Provide Ticket-Specific Context

Now, depending on the output of `classify_transcript()`, we would want to provide different context to the next call - namely, a `billing` ticket would necessitate the details from `get_billing_details()`, a `sale` ticket would want the output of `get_sale_items()` and `get_rewards()`, and a `support_ticket` would require `get_account_details`. We define a second call `handle_ticket()` which calls `classify_transcript()` and calls the correct functions for the scenario via dynamic configuration:



```python
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
```


And there you have it! Let’s see how `handle_ticket` deals with each of the following transcripts:



```python
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
```

    Routed to: billing
    Summary:
    Customer John Doe (email: johndoe@gmail.com) is requesting a refund for a double charge for a TV purchase made a week ago. The customer shows two charges of $349.99 on their bank statement.
    Routed to: sale
    Summary:
    Customer johndoe@gmail.com is interested in purchasing a new monitor and wants to know about discounts. There is a monitor available at half off for $80 and the customer is eligible for an additional 10% off for loyalty rewards.
    Routed to: support
    Summary:
    Customer John Doe (johndoe@gmail.com) forgot their site password and is locked out of their email. They are asking for alternative ways to verify their identity. Security question: Childhood Pet Name, Answer: Piddles.



<div class="admonition tip">
<p class="admonition-title">Additional Real-World Examples</p>
<ul>
<li><b>IT Help Desk</b>: Have LLM determine whether the user request is level 1, 2, or 3 support and route accordingly</li>
<li><b>Software-as-a-Service (SaaS) Companies</b>: A question about how to use a specific feature might be routed to the product support team, while an issue with account access could be sent to the account management team.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider the following:

    - Update the `response_model` to more accurately reflect your use-case.
    - Implement Pydantic `ValidationError` and Tenacity `retry` to improve reliability and accuracy.
    - Evaluate the quality of extraction by using another LLM to verify classification accuracy.
    - Use a local model like Ollama to protect company or other sensitive data.

