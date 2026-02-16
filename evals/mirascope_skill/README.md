# mirascope_skill Eval

Evaluates the Mirascope skill's ability to generate and iteratively improve self-contained Mirascope programs.

## Structure

```
evals/mirascope_skill/
├── skill/
│   ├── SKILL.md          # The skill instructions (what we're evaluating)
│   ├── run_eval.py       # Full eval pipeline (bootstrap → eval → LOO iteration → report)
│   └── template.py       # Reference template program
├── samples/
│   ├── invoice_generator/ # Structured output program sample
│   └── scheduling_agent/  # Tool-based agent program sample
└── results/               # Eval output (gitignored)
```

## Running

```bash
# Run eval for a sample
cd evals/mirascope_skill
MIRASCOPE_API_KEY=... ./skill/run_eval.py \
  --sample samples/invoice_generator/sample_001.yaml \
  --output results/invoice_eval/

# Results
cat results/invoice_eval/report.json
```

## Eval Pipeline

1. **Bootstrap**: Generate a program from the skill using the sample's bootstrap prompt
2. **Initial Eval**: Run all N queries against the generated program, score pass/fail
3. **LOO Iteration**: For each query i, improve the base program using feedback from queries ≠i, then test on query i (unbiased estimation)
4. **Report**: Initial pass rate, post-iteration pass rate, fixed/regressed counts

## Sample Format

YAML files defining:
- `bootstrap.prompt`: What to ask the skill to generate
- `queries[]`: Test queries with `expected` criteria (output_contains, output_excludes, invokes_tools)
- `test_state`: Context for agent samples (today's date, existing appointments)
