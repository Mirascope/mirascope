# mirascope_skill Eval

Evaluates the `mirascope_skill` — specifically, how well `SKILL.md` (the skill instructions) enables an LLM to:

1. **Generate** a working Mirascope program from a natural language request (one-shot)
2. **Improve** that program when given human feedback (iteration)

The skill is the thing under test. The eval measures whether following SKILL.md produces programs that actually work.

## Structure

```
evals/mirascope_skill/
├── skill/
│   ├── SKILL.md          # The skill instructions (what we're evaluating)
│   ├── run_eval.py       # Eval pipeline (subcommands: run, iterate, report)
│   └── template.py       # Reference template program
├── samples/
│   ├── invoice_generator/ # Structured output program sample
│   └── scheduling_agent/  # Tool-based agent program sample
└── results/               # Eval output (gitignored)
```

## Running

```bash
cd evals/mirascope_skill

# 1. Generate program + run all queries (creates traces in Mirascope Cloud)
MIRASCOPE_API_KEY=... ./skill/run_eval.py run \
  --sample samples/invoice_generator/sample_001.yaml \
  --output results/invoice_eval/

# 2. Review traces in Mirascope Cloud, annotate each with pass/fail + reasoning

# 3. Run LKO iteration (reads annotations, improves program, runs held-out queries)
MIRASCOPE_API_KEY=... ./skill/run_eval.py iterate \
  --output results/invoice_eval/ \
  --k 1

# 4. Annotate the new traces

# 5. Compute final report
MIRASCOPE_API_KEY=... ./skill/run_eval.py report \
  --output results/invoice_eval/
```

## Eval Pipeline

### Phase 1 — Bootstrap (one-shot capability)

The skill generates a program from a bootstrap prompt. Generated programs include `ops.configure()` and `@ops.trace` so every execution creates traces in Mirascope Cloud.

### Phase 2 — Run Queries

All N queries run in parallel against the generated program. Each execution creates a trace. The harness matches runs to traces by searching input content.

### Human Scoring

You review the traces in Mirascope Cloud and annotate each with `pass`/`fail` + reasoning. This is the same workflow a real user would follow — running a program, seeing the output, and providing corrective feedback on the trace.

### Phase 3 — LKO Iteration (Leave-K-Out)

For each held-out group of K queries:
- Read annotations from the N-K training traces
- Give the human feedback to the skill along with the **original base program**
- Run the held-out K queries on the improved program (creating new traces)

Critical invariant: every iteration starts from the same base program. This is leave-K-out cross-validation — it gives an unbiased estimate of whether the skill can generalize improvements.

### Human Scoring (round 2)

Annotate the new traces from the iteration phase.

### Phase 4 — Report

Compare initial vs post-iteration pass rates. Count fixed and regressed queries. The delta tells us whether the skill's improvement capability actually helps.

## Sample Format

YAML files defining:
- `bootstrap.prompt`: What to ask the skill to generate
- `queries[]`: Test queries with `id` and `text`
- `test_state`: Context for agent samples (today's date, existing appointments)
- `metadata`: Tags, difficulty, description

The `expected` block in queries is optional documentation — scoring is human-only via trace annotations.
