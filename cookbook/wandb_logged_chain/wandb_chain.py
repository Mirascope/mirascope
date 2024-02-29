"""Main script for logging a chain of prompts to WandB."""
import datetime
from typing import Optional

import wandb
from pydantic_settings import BaseSettings, SettingsConfigDict
from wandb.sdk.data_types.trace_tree import Trace
from wandb_prompts.coolnessprompt import Coolness, CoolnessPrompt
from wandb_prompts.partyinviteprompt import PartyInvitePrompt
from wandb_prompts.whoprompt import Person, WhoPrompt

from mirascope import OpenAIChat


class Settings(BaseSettings):
    """Settings for wandb_logged_chain."""

    wandb_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


if __name__ == "__main__":
    wandb.login(key=settings.wandb_api_key)
    wandb.init(project="wandb_logged_chain")

    root_span = Trace(
        name="root",
        kind="chain",
        start_time_ms=round(datetime.datetime.now().timestamp() * 1000),
        metadata={"user": "mirascope_user"},
    )
    chat = OpenAIChat(api_key=settings.openai_api_key)

    who_prompt = WhoPrompt(span_type="tool", person="Brian")
    who_completion = chat.extract(Person, who_prompt)
    who_span = who_prompt.span(who_completion, root_span)

    coolness_prompt = CoolnessPrompt(span_type="tool", person=who_completion.person)
    coolness_completion = chat.extract(Coolness, coolness_prompt)
    coolness_span = coolness_prompt.span(coolness_completion, who_span)

    party_invite_prompt = PartyInvitePrompt(
        span_type="llm", coolness=coolness_completion.coolness
    )
    party_completion = chat.create(party_invite_prompt)
    party_invite_prompt.span(party_completion, coolness_span)

    root_span._span.end_time_ms = round(datetime.datetime.now().timestamp() * 1000)
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
