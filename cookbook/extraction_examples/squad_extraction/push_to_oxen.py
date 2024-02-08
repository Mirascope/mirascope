"""A script for transforming and uploading geology-squad data for analysis."""
import argparse
import json
import os

import pandas as pd  # type: ignore
from eval import normalize_answer
from oxen import LocalRepo  # type: ignore
from oxen.user import config_user  # type: ignore
from pydantic import BaseModel
from squad import load_geology_squad


class JoinedRow(BaseModel):
    """A transformed row of geology-squad data."""

    id: str
    question: str
    context: str
    answers: list[str]
    extracted_answer: str
    exact_match: bool


def join_geology_squad_with_answers(prompt_version: str):
    """Joins the geology-squad data and versioned answers."""
    questions = load_geology_squad()
    with open(f"geology-squad-answers-{prompt_version}.json") as f:
        extracted_answers = json.load(f)

    columns = list(JoinedRow.model_fields.keys())
    rows = [
        list(
            JoinedRow(
                id=question.id,
                question=question.question,
                context=question.context,
                answers=question.answers,
                extracted_answer=extracted_answers[question.id],
                exact_match=any(
                    normalize_answer(extracted_answers[question.id].lower())
                    == normalize_answer(answer.lower())
                    for answer in question.answers
                ),
            )
            .model_dump()
            .values()
        )
        for question in questions
    ]

    return pd.DataFrame(rows, columns=columns)


def main(prompt_version: str):
    """Uploads the joined geology-squad data and versioned answers."""
    repo = LocalRepo("geology-squad")

    filepath = os.path.join(repo.path, prompt_version)
    if os.path.exists(filepath):
        raise ValueError(f"{filepath} already exists.")

    os.mkdir(filepath)

    df = join_geology_squad_with_answers(prompt_version)

    filename = os.path.join(filepath, "answers.csv")
    with open(filename, "w") as f:
        df.to_csv(f, index=False)

    repo.set_remote("origin", "https://hub.oxen.ai/Mirascope/geology-squad")
    repo.add(filename)
    repo.commit(
        f"Add prompt version {prompt_version} extracted answers joined with questions."
    )
    repo.push()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transform and upload geology-squad data."
    )
    parser.add_argument("prompt_version", help="The version of the prompt.")
    args = parser.parse_args()

    main(args.prompt_version)
