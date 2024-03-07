"""Main script for logging a chain of prompts to WandB."""
import datetime
from typing import Optional

import wandb
from pydantic_settings import BaseSettings, SettingsConfigDict
from wandb.sdk.data_types.trace_tree import Trace
from wandb_prompts.coolness_prompt import Coolness, CoolnessPrompt
from wandb_prompts.party_invite_prompt import PartyInvitePrompt
from wandb_prompts.who_prompt import Person, WhoPrompt


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

    who_prompt = WhoPrompt(
        span_type="tool",
        person="Brian",
        api_key=settings.openai_api_key,
    )
    who_completion, who_span = who_prompt.extract_with_trace(Person, root_span)

    coolness_prompt = CoolnessPrompt(
        span_type="tool", person=who_completion.person, api_key=settings.openai_api_key
    )
    coolness_completion, coolness_span = coolness_prompt.extract_with_trace(
        Coolness, who_span
    )

    party_invite_prompt = PartyInvitePrompt(
        span_type="llm",
        coolness=coolness_completion.coolness,
        api_key=settings.openai_api_key,
    )
    party_completion, party_span = party_invite_prompt.create_with_trace(coolness_span)
    print("\nparty completion:\n", party_completion)

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
