"""This module contains the type definition for the Vertex call keyword arguments."""

from vertexai.generative_models import Content, Tool

from ..base import BaseCallKwargs
from .call_params import VertexCallParams


class VertexCallKwargs(VertexCallParams, BaseCallKwargs[Tool]):
    contents: list[Content]
