"""This module defines the function return type for functions as LLM calls."""

from typing import TypeAlias

from ..openai import AsyncOpenAIDynamicConfig, OpenAIDynamicConfig

AsyncXAIDynamicConfig: TypeAlias = AsyncOpenAIDynamicConfig
XAIDynamicConfig: TypeAlias = OpenAIDynamicConfig
