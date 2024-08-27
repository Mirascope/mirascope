"""This module contains the config dict for response models."""

from pydantic import ConfigDict


class ResponseModelConfigDict(ConfigDict, total=False):
    """An extension of the base `ConfigDict` for configuring response models."""

    strict: bool
