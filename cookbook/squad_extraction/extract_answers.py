"""Extracts answers for SQuAD 2.0 questions using GPT 3.5 Turbo."""
import argparse
import json
import os

from squad import load_geology_squad
from squad_config import Settings
from squad_prompts.question import ExtractedAnswer, Question

settings = Settings()
if settings.openai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key


def main(prompt_version: str):
    """Extracts answers for SQuAD 2.0 questions using GPT 3.5 Turbo."""
    questions = load_geology_squad()
    extracted_answers = {
        question.id: Question(paragraph=question.context, question=question.question)
        .extract(
            ExtractedAnswer,
            retries=2,
        )
        .answer
        for question in questions
    }
    json.dump(
        extracted_answers, open(f"geology-squad-answers-{prompt_version}.json", "w")
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transform and upload geology-squad data."
    )
    parser.add_argument("prompt_version", help="The version of the prompt.")
    args = parser.parse_args()

    main(args.prompt_version)
