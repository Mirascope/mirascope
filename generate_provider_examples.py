import re
from pathlib import Path

from mirascope.llm import Provider
from pydantic import BaseModel


class ProviderInfo(BaseModel):
    """Provider information for UI and substitutions."""

    provider: Provider
    title: str
    model: str


PROVIDER_INFO: dict[Provider, ProviderInfo] = {
    "openai": ProviderInfo(provider="openai", title="OpenAI", model="gpt-4o-mini"),
    "anthropic": ProviderInfo(
        provider="anthropic", title="Anthropic", model="claude-3-5-sonnet-latest"
    ),
    "google": ProviderInfo(provider="google", title="Google", model="gemini-2.0-flash"),
    "groq": ProviderInfo(
        provider="groq", title="Groq", model="llama-3.3-70b-versatile"
    ),
    "xai": ProviderInfo(provider="xai", title="xAI", model="grok-3"),
    "mistral": ProviderInfo(
        provider="mistral", title="Mistral", model="mistral-large-latest"
    ),
    "cohere": ProviderInfo(provider="cohere", title="Cohere", model="command-r-plus"),
    "litellm": ProviderInfo(provider="litellm", title="LiteLLM", model="gpt-4o-mini"),
    "azure": ProviderInfo(provider="azure", title="Azure AI", model="gpt-4o-mini"),
    "bedrock": ProviderInfo(
        provider="bedrock",
        title="Bedrock",
        model="amazon.nova-lite-v1:0",
    ),
}


def substitute_provider_import(content: str, provider: Provider) -> str:
    """Substitute provider in import statement."""
    return re.sub(
        r"(from mirascope.core import .*?)openai(.*?)",
        rf"\1{provider}\2",
        content,
    )


def substitute_provider_type(content: str, provider: Provider) -> str:
    """Substitute provider in type names (e.g. openai.OpenAICallResponse)."""
    provider_name = provider.capitalize()

    if provider == "litellm":
        provider_name = "LiteLLM"
    if provider == "openai":
        provider_name = "OpenAI"

    return re.sub(
        r"openai\.OpenAI",
        f"{provider}.{provider_name}",
        content,
    )


def substitute_llm_call_decorator(content: str, provider: Provider) -> str:
    """Substitute provider and model into @llm.call decorator."""
    subs = PROVIDER_INFO[provider]

    # Use regex with re.DOTALL to match across lines
    decorator_pattern = r"@llm\.call\((.*?)\)"

    def replace_decorator(match: re.Match) -> str:
        decorator_args = match.group(1)

        # Check if we found the expected parameters
        if 'provider="openai"' not in decorator_args:
            raise ValueError(
                f"Could not find provider='openai' in decorator: {decorator_args}"
            )
        if 'model="gpt-4o-mini"' not in decorator_args:
            raise ValueError(
                f"Could not find model='gpt-4o-mini' in decorator: {decorator_args}"
            )

        # Make substitutions, preserving whitespace
        updated_args = decorator_args.replace(
            'provider="openai"', f'provider="{subs.provider}"'
        ).replace('model="gpt-4o-mini"', f'model="{subs.model}"')

        return f"@llm.call({updated_args})"

    # Perform substitution with re.DOTALL flag
    new_content, _ = re.subn(
        decorator_pattern, replace_decorator, content, flags=re.DOTALL
    )

    return new_content


def substitute_llm_override(content: str, provider: Provider) -> str:
    """Substitute provider and model into llm.override function."""
    replacement_provider = "openai" if provider == "anthropic" else "anthropic"
    subs = PROVIDER_INFO[replacement_provider]

    # Use regex with re.DOTALL to match across lines
    override_pattern = r"llm\.override\((.*?)\)"

    def replace_override(match: re.Match) -> str:
        override_args = match.group(1)

        # Check if we found the expected parameters
        if 'provider="anthropic"' not in override_args:
            raise ValueError(
                f"Could not find provider='anthropic' in override: {override_args}"
            )
        if 'model="claude-3-5-sonnet-latest"' not in override_args:
            raise ValueError(
                f"Could not find model='claude-3-5-sonnet-latest' in override: {override_args}"
            )

        # Make substitutions, preserving whitespace
        updated_args = override_args.replace(
            'provider="anthropic"', f'provider="{subs.provider}"'
        ).replace('model="claude-3-5-sonnet-latest"', f'model="{subs.model}"')

        return f"llm.override({updated_args})"

    # Perform substitution with re.DOTALL flag
    new_content, _ = re.subn(
        override_pattern, replace_override, content, flags=re.DOTALL
    )

    return new_content


def substitute_provider_specific_content(content: str, provider: Provider) -> str:
    """Apply all provider-specific substitutions."""
    if provider not in PROVIDER_INFO:
        raise ValueError(f"Provider {provider} not found in {PROVIDER_INFO}")

    content = substitute_llm_call_decorator(content, provider)
    content = substitute_provider_import(content, provider)
    content = substitute_provider_type(content, provider)
    content = substitute_llm_override(content, provider)
    return content


SNIPPETS_DIR = Path("build/snippets")


def get_supported_providers() -> list[ProviderInfo]:
    return list(PROVIDER_INFO.values())


def generate_provider_examples(
    *, example_dirs: list[str], examples_root: Path, snippets_dir: Path
) -> None:
    """Generate provider-specific examples for python files in configured paths."""
    # Clear/create snippets directory
    if snippets_dir.exists():
        for file in snippets_dir.rglob("*.py"):
            file.unlink()
    snippets_dir.mkdir(exist_ok=True, parents=True)
    supported_providers = get_supported_providers()

    for example_dir in example_dirs:
        source_dir = examples_root / example_dir

        for info in supported_providers:
            provider_name = info.provider
            output_dir = snippets_dir / example_dir / provider_name
            output_dir.mkdir(parents=True, exist_ok=True)

            for base_file in source_dir.glob("*.py"):
                content = base_file.read_text()
                output = substitute_provider_specific_content(content, provider_name)

                out_file = output_dir / base_file.name
                out_file.write_text(output)

            for override_file in (source_dir / provider_name).glob("*.py"):
                # If there was a file specified for this provider, use it,
                # potentially overriding the default content.
                content = override_file.read_text()
                out_file = output_dir / override_file.name
                out_file.write_text(content)
