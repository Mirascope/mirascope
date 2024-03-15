"""A module for interacting with OpenAI models."""
from contextlib import suppress

with suppress(ImportError):
    from . import wandb

from .calls import OpenAICall
from .extractors import OpenAIExtractor
from .tools import OpenAITool
from .types import OpenAICallParams, OpenAICallResponse, OpenAICallResponseChunk
