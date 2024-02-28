"""Extracts answers for SQuAD 2.0 questions using GPT 3.5 Turbo."""
import argparse
import json

from squad import load_geology_squad
from squad_config import Settings
from squad_prompts.question import ExtractedAnswer, QuestionPrompt

from mirascope import OpenAIChat

settings = Settings()


def main(prompt_version: str):
    """Extracts answers for SQuAD 2.0 questions using GPT 3.5 Turbo."""
    chat = OpenAIChat(api_key=settings.openai_api_key)
    questions = load_geology_squad()
    extracted_answers = {
        question.id: chat.extract(
            ExtractedAnswer,
            QuestionPrompt(paragraph=question.context, question=question.question),
            retries=2,
        ).answer
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
