"""Bootstrap eval: generate a program from a sample, run queries, save results.

Usage:
    python -m harness.run_bootstrap --sample YAML --output DIR [--model MODEL]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mirascope import llm, ops
from pydantic import BaseModel

from .models import BootstrapResult, EvalSample, QueryResult
from .program import get_schema, run_program, validate_program

SKILL_MD = Path(__file__).resolve().parent.parent / "skill" / "SKILL.md"
DEFAULT_MODEL = "anthropic/claude-sonnet-4-5"


# ---------------------------------------------------------------------------
# LLM helpers
# ---------------------------------------------------------------------------


class GeneratedProgram(BaseModel):
    code: str


@ops.trace(tags=["eval", "bootstrap", "generate"])
@llm.call(DEFAULT_MODEL, format=GeneratedProgram)
def generate_program(skill_instructions: str, bootstrap_prompt: str) -> str:
    return f"""You are a Mirascope program generator. Follow the skill instructions exactly.

<skill_instructions>
{skill_instructions}
</skill_instructions>

Create a complete, self-contained Mirascope program for the following request:

<request>
{bootstrap_prompt}
</request>

Return the full Python source code. The program must:
1. Use PEP 723 inline script metadata with dependencies
2. Define ProgramInput and ProgramOutput Pydantic models with Field descriptions
3. Support --help, --schema, and --input CLI flags
4. Use @ops.trace, @ops.version, and @llm.call decorators
5. Include ops.configure() and ops.instrument_llm() at module level"""


class OrchestrationResult(BaseModel):
    input_json: dict
    reasoning: str


@ops.trace(tags=["eval", "bootstrap", "orchestrate"])
@llm.call(DEFAULT_MODEL, format=OrchestrationResult)
def orchestrate_query(query_text: str, input_schema: dict) -> str:
    return f"""You are an orchestration layer that translates natural language queries into structured JSON input for a program.

The program accepts input matching this JSON schema:
{json.dumps(input_schema, indent=2)}

Translate the following user query into a valid JSON object matching the schema above.
If information is missing, use reasonable defaults. If the query doesn't relate to this program's purpose, set input_json to an empty object {{}}.

User query:
{query_text}

Return the structured input as input_json and explain your reasoning."""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap eval: generate program from sample and run queries"
    )
    parser.add_argument("--sample", required=True, help="Path to YAML eval sample")
    parser.add_argument("--output", required=True, help="Output directory for results")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"LLM model (default: {DEFAULT_MODEL})")
    args = parser.parse_args()

    sample = EvalSample.from_yaml(args.sample)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read skill instructions
    skill_instructions = SKILL_MD.read_text()

    # Override model if specified
    if args.model != DEFAULT_MODEL:
        generate_program.__wrapped__.__func__._model = args.model  # type: ignore[attr-defined]

    print(f"Generating program for sample: {sample.sample_id}")

    # Step 1: Generate program
    with ops.session(id=f"eval-bootstrap-{sample.sample_id}"):
        response = generate_program(skill_instructions, sample.bootstrap.prompt)
        program_code = response.parse().code

    # Write program
    program_path = output_dir / "program.py"
    program_path.write_text(program_code)
    print(f"Program written to: {program_path}")

    # Step 2: Validate
    valid, error = validate_program(program_path)
    if not valid:
        print(f"Program validation failed: {error}", file=sys.stderr)
        # Save partial result even on failure
        result = BootstrapResult(
            sample_id=sample.sample_id,
            program_path=str(program_path),
            program_code=program_code,
            query_results=[
                QueryResult(query_id=q.id, error=f"Program invalid: {error}")
                for q in sample.queries
            ],
        )
        result_path = output_dir / "bootstrap_results.json"
        result.save(result_path)
        print(f"Partial results saved to: {result_path}")
        sys.exit(1)

    print("Program validated successfully")

    # Step 3: Get schema
    schema = get_schema(program_path)
    input_schema = schema["input"]
    print(f"Input schema: {json.dumps(input_schema, indent=2)}")

    # Step 4: Run queries
    query_results: list[QueryResult] = []
    for query in sample.queries:
        print(f"\nRunning query {query.id}: {query.text[:80]}...")

        try:
            # Orchestrate: NL → structured input
            with ops.session(id=f"eval-bootstrap-{sample.sample_id}"):
                orch_response = orchestrate_query(query.text, input_schema)
                orch = orch_response.parse()
                orchestrated_input = orch.input_json
                print(f"  Orchestrated input: {json.dumps(orchestrated_input)[:120]}")
        except Exception as e:
            query_results.append(QueryResult(
                query_id=query.id,
                error=f"Orchestration failed: {e}",
            ))
            continue

        try:
            # Run program
            input_json_str = json.dumps(orchestrated_input)
            stdout, stderr = run_program(program_path, input_json_str)

            if stderr and not stdout:
                query_results.append(QueryResult(
                    query_id=query.id,
                    orchestrated_input=orchestrated_input,
                    raw_output=stderr,
                    error=f"Program error: {stderr[:500]}",
                ))
            else:
                query_results.append(QueryResult(
                    query_id=query.id,
                    orchestrated_input=orchestrated_input,
                    raw_output=stdout,
                ))
                print(f"  Output: {stdout[:120]}")
        except Exception as e:
            query_results.append(QueryResult(
                query_id=query.id,
                orchestrated_input=orchestrated_input,
                error=f"Program execution failed: {e}",
            ))

    # Step 5: Save results
    result = BootstrapResult(
        sample_id=sample.sample_id,
        program_path=str(program_path),
        program_code=program_code,
        query_results=query_results,
    )
    result_path = output_dir / "bootstrap_results.json"
    result.save(result_path)
    print(f"\nResults saved to: {result_path}")
    print(f"Queries run: {len(query_results)}")
    print(f"Errors: {sum(1 for r in query_results if r.error)}")


if __name__ == "__main__":
    main()
