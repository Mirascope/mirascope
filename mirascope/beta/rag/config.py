from typing import Callable

from pydantic import BaseModel


class BaseConfig(BaseModel):
    llm_ops: list[Callable | str] = []
    client_wrappers: list[Callable | str] = []
