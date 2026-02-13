#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["mirascope[anthropic,ops]", "pydantic"]
# ///
"""Template Mirascope program — replace with your own logic."""
import argparse
import json
import sys

from pydantic import BaseModel, Field
from mirascope import llm, ops


# --- Input/Output Models ---


class ProgramInput(BaseModel):
    """Structured input for this program."""

    prompt: str = Field(description="The user's request")


class ProgramOutput(BaseModel):
    """Structured output from this program."""

    result: str = Field(description="The generated result")


# --- Mirascope Setup ---

ops.configure()
ops.instrument_llm()


@ops.trace(tags=["template"])
@ops.version
@llm.call("anthropic/claude-sonnet-4-5", format=ProgramOutput)
def run(input_data: ProgramInput) -> str:
    return f"Process this request: {input_data.prompt}"


# --- CLI ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Template Mirascope program")
    parser.add_argument(
        "--input", required=False, help="JSON string matching ProgramInput schema"
    )
    parser.add_argument(
        "--schema",
        action="store_true",
        help="Print I/O JSON schemas and exit",
    )
    args = parser.parse_args()

    if args.schema:
        print(
            json.dumps(
                {
                    "input": ProgramInput.model_json_schema(),
                    "output": ProgramOutput.model_json_schema(),
                },
                indent=2,
            )
        )
        sys.exit(0)

    if not args.input:
        parser.error("--input is required (unless using --schema)")

    data = ProgramInput.model_validate_json(args.input)
    response = run(data)
    print(response.parse().model_dump_json(indent=2))
