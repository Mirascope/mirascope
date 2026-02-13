"""Pydantic models for eval samples, results, and annotations."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Eval sample (loaded from YAML)
# ---------------------------------------------------------------------------


class QueryExpected(BaseModel):
    invokes_skill: bool
    output_contains: list[str] = []
    output_excludes: list[str] = []
    semantic_requirements: list[str] = []


class EvalQuery(BaseModel):
    id: str
    text: str
    specificity: str
    professionalism: str
    expected: QueryExpected


class Bootstrap(BaseModel):
    prompt: str
    specificity: str
    professionalism: str
    expected_capabilities: list[str]


class SampleMetadata(BaseModel):
    description: str = ""
    tags: list[str] = []
    difficulty: str = "medium"


class EvalSample(BaseModel):
    version: str
    skill_type: str
    sample_id: str
    created_at: str = ""
    metadata: SampleMetadata = SampleMetadata()
    bootstrap: Bootstrap
    queries: list[EvalQuery]

    @classmethod
    def from_yaml(cls, path: str | Path) -> EvalSample:
        with open(path) as f:
            return cls.model_validate(yaml.safe_load(f))


# ---------------------------------------------------------------------------
# Results (persisted as JSON)
# ---------------------------------------------------------------------------


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
    def load(cls, path: str | Path) -> BootstrapResult:
        return cls.model_validate_json(Path(path).read_text())


class FoldResult(BaseModel):
    fold_index: int
    held_out_query_id: str
    program_code: str
    query_result: QueryResult
    annotation: Annotation | None = None


class IterationResult(BaseModel):
    sample_id: str
    folds: list[FoldResult]

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, path: str | Path) -> IterationResult:
        return cls.model_validate_json(Path(path).read_text())
