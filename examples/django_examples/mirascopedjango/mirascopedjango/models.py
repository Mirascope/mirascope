"""
Mirascope Pydantic models go here along with Django models
"""

from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str
