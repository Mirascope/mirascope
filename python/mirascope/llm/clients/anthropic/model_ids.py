"""Anthropic registered LLM models."""

from typing import TypeAlias

import anthropic

AnthropicModelId: TypeAlias = anthropic.types.Model
"""The Anthropic model ids registered with Mirascope."""
