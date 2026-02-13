#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mirascope[all]==2.2.2",
#     "pydantic>=2.0",
#     "pyyaml>=6.0",
# ]
# ///
"""Bootstrap eval: generate a program from a sample, run queries, save results.

Usage:
    ./run_bootstrap.py --sample SAMPLE.yaml --output DIR [--model MODEL]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml
from mirascope import llm, ops
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class QueryExpected(BaseModel):
    invokes_skill: bool = True
    output_contains: list[str] = []
    output_excludes: list[str] = []
    semantic_requirements: list[str] = []


class EvalQuery(BaseModel):
    id: str
    text: str
    specificity: str = ""
    professionalism: str = ""
    expected: QueryExpected = Field(default_factory=QueryExpected)


class Bootstrap(BaseModel):
    prompt: str
    specificity: str = ""
    professionalism: str = ""
    expected_capabilities: list[str] = []


class SampleMetadata(BaseModel):
    description: str = ""
    tags: list[str] = []
    difficulty: str = "medium"


class EvalSample(BaseModel):
    version: str = "1.0"
    skill_type: str
    sample_id: str
    created_at: str = ""
    metadata: SampleMetadata = Field(default_factory=SampleMetadata)
    bootstrap: Bootstrap
    queries: list[EvalQuery]

    @classmethod
    def from_yaml(cls, path: str | Path) -> "EvalSample":
        with open(path) as f:
            return cls.model_validate(yaml.safe_load(f))


class QueryResult(BaseModel):
    query_id: str
    orchestrated_input: dict | None = None
    raw_output: str = ""
    trace_id: str | None = None
    span_id: str | None = None
    error: str | None = None


class Annotation(BaseModel):
    query_id: str
    acceptable: bool
    feedback: str = ""


class BootstrapResult(BaseModel):
    sample_id: str
    program_path: str
    program_code: str
    query_results: list[QueryResult]
    annotations: list[Annotation] = []

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "BootstrapResult":
        return cls.model_validate_json(Path(path).read_text())


# ---------------------------------------------------------------------------
# Program helpers
# ---------------------------------------------------------------------------


def _run_uv(program_path: str | Path, *args: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    return subprocess.run(
        ["uv", "run", str(program_path), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def validate_program(program_path: str | Path) -> tuple[bool, str]:
    """Run --help and --schema to verify the program is well-formed."""
    path = Path(program_path)
    if not path.exists():
        return False, f"Program file not found: {path}"

    try:
        result = _run_uv(path, "--help")
        if result.returncode != 0:
            return False, f"--help failed: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "--help timed out"

    try:
        result = _run_uv(path, "--schema")
        if result.returncode != 0:
            return False, f"--schema failed: {result.stderr}"
        schema = json.loads(result.stdout)
        if "input" not in schema or "output" not in schema:
            return False, f"--schema missing 'input' or 'output' keys: {list(schema.keys())}"
    except subprocess.TimeoutExpired:
        return False, "--schema timed out"
    except json.JSONDecodeError as e:
        return False, f"--schema returned invalid JSON: {e}"

    return True, ""


def get_schema(program_path: str | Path) -> dict:
    """Run --schema and return the parsed JSON."""
    result = _run_uv(program_path, "--schema")
    if result.returncode != 0:
        raise RuntimeError(f"--schema failed: {result.stderr}")
    return json.loads(result.stdout)


def run_program(program_path: str | Path, input_json: str, timeout: int = 120) -> tuple[str, str]:
    """Run --input and return (stdout, stderr)."""
    result = _run_uv(program_path, "--input", input_json, timeout=timeout)
    return result.stdout, result.stderr


# ---------------------------------------------------------------------------
# LLM calls
# ---------------------------------------------------------------------------

SKILL_MD = Path(__file__).resolve().parent / "SKILL.md"
DEFAULT_MODEL = "anthropic/claude-sonnet-4-5"


class GeneratedProgram(BaseModel):
    code: str = Field(description="Complete Python source code for the program")


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
4. Use @ops.trace and @llm.call decorators
5. Include ops.configure() and ops.instrument_llm() at module level
6. Follow all robustness patterns from the skill instructions"""


class OrchestrationResult(BaseModel):
    input_json: dict = Field(description="Structured input matching the program's schema")
    reasoning: str = Field(description="Explanation of how the query was translated")


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

    # Initialize tracing (requires MIRASCOPE_API_KEY)
    ops.configure()
    ops.instrument_llm()

    sample = EvalSample.from_yaml(args.sample)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    skill_instructions = SKILL_MD.read_text()

    print(f"Generating program for sample: {sample.sample_id}")

    # Step 1: Generate program
    with ops.session(id=f"eval-bootstrap-{sample.sample_id}"):
        response = generate_program(skill_instructions, sample.bootstrap.prompt)
        program_code = response.parse().code

    program_path = output_dir / "program.py"
    program_path.write_text(program_code)
    print(f"Program written to: {program_path}")

    # Step 2: Validate
    valid, error = validate_program(program_path)
    if not valid:
        print(f"Program validation failed: {error}", file=sys.stderr)
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
