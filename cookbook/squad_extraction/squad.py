"""Utility functions for loading and transforming the geology-squad.json data.

This recipe uses a modified version of the SQuAD 2.0 Dev dataset. Primary modifications
include a restriction to a single article (Geology) and the removal of all questions
marked as unanswerable. This results in a total of 116 questions.

The modified version of the dataset is available on our GitHub:
https://raw.githubusercontent.com/Mirascope/datasets/main/geology-squad.json
"""
import json
import os
from urllib import request

from pydantic import BaseModel


class Answer(BaseModel):
    """The answer to a question about a paragraph of text."""

    text: str
    answer_start: int


class Question(BaseModel):
    """A question about a paragraph of text."""

    question: str
    id: str
    answers: list[Answer]
    is_impossible: bool


class Paragraph(BaseModel):
    """A paragraph of text with questions and answers."""

    context: str
    qas: list[Question]


class SquadDataset(BaseModel):
    """The SQuAD 2.0 Dev dataset schema."""

    title: str
    paragraphs: list[Paragraph]


class QuestionWithContext(BaseModel):
    """A question with it's answers and context."""

    id: str
    question: str
    context: str
    answers: list[str]


def load_geology_squad() -> list[QuestionWithContext]:
    """Returns geology-squad.json dataset loaded from GitHub as `SquadDataset`."""
    url = "https://raw.githubusercontent.com/Mirascope/datasets/main/geology-squad.json"
    if not os.path.exists("geology-squad.json"):
        with request.urlopen(url) as response:
            json_data = json.load(response)
            json.dump(json_data, open("geology-squad.json", "w"))
    else:
        with open("geology-squad.json") as f:
            json_data = json.load(f)

    dataset = SquadDataset.model_validate(json_data["data"][0])
    return [
        QuestionWithContext(
            id=qas.id,
            question=qas.question,
            context=paragraph.context,
            answers=[answer.text for answer in qas.answers],
        )
        for paragraph in dataset.paragraphs
        for qas in paragraph.qas
    ]
