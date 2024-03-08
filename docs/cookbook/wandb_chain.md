# Logging Prompt Chains with Weights and Biases

This recipe will show you:

- how to use Mirascope’s Weights & Biases integrated [`WandbPrompt`](https://github.com/Mirascope/mirascope/blob/main/mirascope/wandb/prompt.py) for easy logging
- take advantage of our [extraction](https://docs.mirascope.io/latest/features/prompt/extracting_structured_information) functionality to streamline the flow of data at each step of the chain.

For the purposes of this example, we take a silly premise where we want to:

1. Find out who we’re talking about from some given context
2. Figure out how cool they are
3. Determine based off their coolness if they should be let into the party.

First we will log the 3-step chain using just Weight and Biases. Then we will show how we can streamline the original code using Mirascope. If you are only interested in the Mirascope section, feel free to skip to the Mirascope integration below.

Before we get started, make sure to have API Keys for both [OpenAI](https://openai.com/blog/openai-api) and [Weights and Biases](https://wandb.ai/site).

## 3-step chain with only W&B

This following example is adapted from the example in the Weights and Biases [documentation](https://docs.wandb.ai/guides/prompts):

```python
import datetime
import openai
import wandb
from wandb.dsk.data_types.trace_tree import Trace

# W&B setup
wandb.login(key=settings.wandb_api_key)
wandb.init(project="wandb_logged_chain")

# Initialize root span for the chain of prompts
root_span = Trace(
  name="root",
  kind="chain",
  start_time_ms=get_time_in_ms(),
  metadata={"user": "some_user"},
)

# Helper function to track start/end times
def get_time_in_ms() -> int:
    """Returns current time in milliseconds."""
    return round(datetime.datetime.now().timestamp() * 1000)

model_name = "gpt-3.5-turbo-1106"
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

"""First step of chain"""
# OpenAI call
person = "Brian"
who_messages = [
	{"role": "system", "content": "Give me the name as one word."}
	{"role": "user", "content": f"{person} is writing some code examples. "
	"Based on the sentence above, what is the name of the person?"}
}
start_time = get_time_in_ms()
who_completion = client.chat.completions.create(
	model=model,
	messages=who_messages
)
end_time = get_time_in_ms()
who = who_completion.choices[0].message

# Trace setup and linking
who_span = Trace(
	name="who_completion",
	kind="llm",
	status_code="success",
	status_message=(None,),
	start_time_ms=start_time,
	end_time_ms=end_time,
	inputs={message["role"]: message["content"] for message in self.messages},
	outputs=who
)
root_span.add_child(who_span)

"""Second step of chain"""
# OpenAI call
coolness_messages = [
	{"role": "system", "content": "You determine coolness on a scale of"
	"1 to 10. If the person's name is Brian, they get an automatic 10 out"
	" of 10. Otherwise, they get a random whole number between 1 and 9."
	"respond with just the number for the rating, nothing else."},
	{"role": "user", "content": f"How cool is {who}?"}
]
start_time = get_time_in_ms()
coolness_completion = client.chat.completions.create(
	model=model,
	messages=coolness_messages
)
end_time = get_time_in_ms()
coolness = coolness_completion.choices[0].message

# Trace setup and linking
coolness_span = Trace(
	name="coolness_completion",
	kind="llm",
	status_code="success",
	status_message=(None,),
	start_time_ms=start_time,
	end_time_ms=end_time,
	inputs={message["role"]: message["content"] for message in self.messages},
	outputs=coolness
)
who_span.add_child(coolness_span)

"""Third step of chain"""
# OpenAI call
invite_messages = [
	{"role": "system", "content": "You're a bouncer and you let people into"
	"the party only if they're at least somewhat cool."},
	{"role": "user", "content": f"If I were to say how cool this person is"
	f"out of 10, I'd say {coolness}. Should they be let into the party?"}
]
start_time = get_time_in_ms()
invite_completion = client.chat.completions.create(
	model=model,
	messages=invite_messages
)
end_time = get_time_in_ms()
invite = invite_completion.choices[0].message

# Trace setup and linking
invite_span = Trace(
	name="invite_completion",
	kind="llm",
	status_code="success",
	status_message=(None,),
	start_time_ms=start_time,
	end_time_ms=end_time,
	inputs={message["role"]: message["content"] for message in self.messages},
	outputs=coolness
)
coolness_span.add_child(invite_span)

# Log the results
root_span._span.end_time_ms = get_time_in_ms()
root_span.add_inputs_and_outputs(
  inputs={
		"query1": who_messages[0],
		"query2": coolness_messages[0],
		"query3": invite_messages[0]
	},
	outputs={"result": invite}
)
root_span.log(name="mirascope_trace")
```

We have to manually calculate start and end times for each call to OpenAI. Furthermore, GPT responses contain lots of filler text (”Your name is Brian” instead of just “Brian”) so we have to use system messages to massage the output in a way that fits smoothly into the next prompt, and just hope for the best.  

## Integration with Mirascope

Mirascope provides a `WandbPrompt` class which can be inherited by any Mirascope `Prompt` , giving access to:

- methods which interally create and link a W&B `Trace` when creating chat completions and extractions
- automatically passing in the entire `Prompt.call_params` field so you can get every detail of your api logged to W&B.
- an overall cleaner interface to interact with OpenAI's GPT.

Wait, did someone say extractions? Mirascope provides extraction functionality, which let you structure output and pass information along an LLM chain much more smoothly. Let’s define the prompts as well as their extraction models in 3 files within a directory `/wandb_prompts`:

```python
# who_prompt.py

from pydantic import BaseModel
from mirascope.wandb import WandbPrompt

class Person(BaseModel):
    """Person model."""

    person: str


class Who(WandbPrompt):
    """Who is {person}?"""

    person: str
```

```python
# coolness_prompt.py

from pydantic import BaseModel
from mirascope.wandb import WandbPrompt

class CoolRating(BaseModel):
    """Coolness rating out of 10."""

    coolness: int


class Coolness(WandbPrompt):
    """
    SYSTEM: You determine coolness on a scale of 1 to 10. If the person's name is Brian,
    they get an automatic 10 out of 10, otherwise, they get a random whole number
    between 1 and 9.

    USER: How cool is {person}?
    """

    person: str
```

```python
# party_invite_prompt.py

from mirascope.wandb import WandbPrompt

class PartyInvite(WandbPrompt):
    """
    SYSTEM:
    You're a bouncer and you decide if people are allowed into the party. You only let
    people in if they're at least somewhat cool.

    USER:
    This person is {coolness} out of 10 cool. Should they be let into the party?
    """

    coolness: int
```

With the prompts written out, the main script becomes much simpler. First, we still need to set up W&B and initialize our root_span:

```python
# wandb_chain.py

import datetime
import os
from typing import Optional

import wandb
from pydantic_settings import BaseSettings, SettingsConfigDict
from wandb.sdk.data_types.trace_tree import Trace
from wandb_prompts.coolness_prompt import Coolness, CoolRating
from wandb_prompts.party_invite_prompt import PartyInvite
from wandb_prompts.who_prompt import Person, Who


class Settings(BaseSettings):
    """Settings for wandb_logged_chain."""

    wandb_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
if settings.openai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key


if __name__ == "__main__":
    wandb.login(key=settings.wandb_api_key)
    wandb.init(project="wandb_logged_chain")

    root_span = Trace(
        name="root",
        kind="chain",
        start_time_ms=round(datetime.datetime.now().timestamp() * 1000),
        metadata={"user": "mirascope_user"},
    )

```

Now, all we need to do is create an instance of each prompt and use the integrated functions `create_with_trace()` or `extract_with_trace()` - these methods call GPT then create a `Trace` affiliated with each completion, which can be linked to a parent span if desired through the `parent` parameter.

```python
# wandb_chain.py
# continued within main:

    who_prompt = Who(span_type="tool", person="Brian")
    who_completion, who_span = who_prompt.extract_with_trace(
        schema=Person, parent=root_span
    )

    coolness_prompt = Coolness(span_type="tool", person=who_completion.person)
    coolness_completion, coolness_span = coolness_prompt.extract_with_trace(
        schema=CoolRating, parent=who_span
    )

    party_invite_prompt = PartyInvite(
        span_type="llm", coolness=coolness_completion.coolness
    )
    party_completion, party_span = party_invite_prompt.create_with_trace(
        parent=coolness_span,
    )

    root_span._span.end_time_ms = party_span._span.end_time_ms
    root_span.add_inputs_and_outputs(
        inputs={
            "query1": str(who_prompt),
            "query2": str(coolness_prompt),
            "query3": str(party_invite_prompt),
        },
        outputs={
            "result1": str(who_completion),
            "result2": str(coolness_completion),
            "result3": str(party_completion),
        },
    )
    root_span.log(name="mirascope_trace")
```
All done - you should now see the logs with a local directory, as well as have access to them online via [W&B](https://wandb.ai/home).
