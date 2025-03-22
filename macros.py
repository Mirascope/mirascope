import builtins
from typing import Any


def define_env(env: Any) -> None:
    @env.filter
    def provider_dir(provider: Any) -> str:
        # Convert to lowercase
        lower_provider = provider.lower()
        # Split by spaces or hyphens and take the first part
        first_word = lower_provider.split()[0]
        return first_word

    @env.macro
    def upper(v: str) -> str:
        return v.upper()

    @env.macro
    def zip(*args: list) -> Any:
        return builtins.zip(*args, strict=True)
