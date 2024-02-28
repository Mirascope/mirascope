"""Main script for logging a chain of prompts to WandB."""

from wandb_utils import Settings, get_time_in_ms
from wandb_prompts.coolnessprompt import Coolness, CoolnessPrompt
from wandb_prompts.partyinviteprompt import PartyInvitePrompt
from wandb_prompts.whoprompt import Person, WhoPrompt

import wandb
from mirascope import OpenAIChat
from wandb.sdk.data_types.trace_tree import Trace

settings = Settings()


if __name__ == "__main__":
    wandb.login(key=settings.wandb_api_key)
    wandb.init(project="wandb_logged_chain")

    root_span = Trace(
        name="root",
        kind="chain",
        start_time_ms=get_time_in_ms(),
        metadata={"user": "mirascope_user"},
    )
    chat = OpenAIChat(api_key=settings.openai_api_key)

    who_prompt = WhoPrompt(span_type="tool", person="Brian")
    start_time = get_time_in_ms()
    who_completion = chat.extract(Person, who_prompt)
    who_span = who_prompt.span(who_completion, root_span, start_time)

    coolness_prompt = CoolnessPrompt(span_type="tool", person=who_completion.person)
    start_time = get_time_in_ms()
    coolness_completion = chat.extract(Coolness, coolness_prompt)
    coolness_span = coolness_prompt.span(coolness_completion, who_span, start_time)

    party_invite_prompt = PartyInvitePrompt(
        span_type="llm", coolness=coolness_completion.coolness
    )
    start_time = get_time_in_ms()
    party_completion = chat.create(party_invite_prompt)
    party_invite_prompt.span(party_completion, coolness_span, start_time)

    root_span._span.end_time_ms = get_time_in_ms()
    root_span.add_inputs_and_outputs(
        inputs={"query": str(who_prompt)}, outputs={"result": str(party_completion)}
    )
    root_span.log(name="mirascope_trace")
