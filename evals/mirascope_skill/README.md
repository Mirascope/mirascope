# mirascope_skill Eval

Evaluates the `mirascope_skill` — specifically, how well `SKILL.md` (the skill instructions) enables an LLM to:

1. **Generate** a working Mirascope program from a natural language request (one-shot)
2. **Improve** that program when given feedback about failures (iteration)

The skill is the thing under test. The eval measures whether following SKILL.md produces programs that actually work.

## Structure

```
evals/mirascope_skill/
├── skill/
│   ├── SKILL.md          # The skill instructions (what we're evaluating)
│   ├── run_eval.py       # Full eval pipeline
│   └── template.py       # Reference template program
├── samples/
│   ├── invoice_generator/ # Structured output program sample
│   └── scheduling_agent/  # Tool-based agent program sample
└── results/               # Eval output (gitignored)
```

## Running

```bash
cd evals/mirascope_skill
MIRASCOPE_API_KEY=... ./skill/run_eval.py \
  --sample samples/invoice_generator/sample_001.yaml \
  --output results/invoice_eval/
```

## Eval Pipeline

### Phase 1 — Bootstrap (one-shot capability)

We give the skill a bootstrap prompt ("build me a scheduling agent" or "build me an invoice generator") and it produces a program. We validate the program structurally (does `--help` work, does `--schema` return valid JSON with input/output).

This tells us: **can the skill produce a syntactically valid, runnable program?**

### Phase 2 — Initial Eval (functional correctness)

We run N queries against the generated program. Each query has expected criteria — output should contain certain strings, should invoke certain tools, shouldn't contain certain things. We score pass/fail for each.

This gives us the **initial pass rate** — the one-shot quality of the skill.

### Phase 3 — LOO Iteration (improvement capability)

For each query i (1 to N):
- Collect feedback from the other N-1 queries (their pass/fail results, what was expected vs what happened)
- Give that feedback to the skill along with the **original base program** and ask it to improve
- Run **only** query i on the improved program
- Record whether it passes

Critical invariant: every iteration starts from the same base program. We never chain improvements. This is leave-one-out cross-validation — it gives us an unbiased estimate of post-iteration performance without leaking the held-out query's information into the improvement step.

This gives us the **post-iteration pass rate** — how well the skill can improve programs based on feedback.

### Phase 4 — Report

Compare initial vs post-iteration pass rates. Count fixed (was failing, now passing) and regressed (was passing, now failing). The delta tells us whether the skill's improvement capability actually helps.

### What the metrics mean

- **High initial pass rate** → skill generates good programs out of the box
- **Positive delta** → skill can effectively learn from feedback
- **Regressions** → skill's improvements are destructive
- **No improvement on failures** → skill's improvement instructions are weak or feedback format is poor

## Sample Format

YAML files defining:
- `bootstrap.prompt`: What to ask the skill to generate
- `queries[]`: Test queries with `expected` criteria (`output_contains`, `output_excludes`, `invokes_tools`)
- `test_state`: Context for agent samples (today's date, existing appointments)
- `metadata`: Tags, difficulty, description
