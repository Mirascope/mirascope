# Mirascope Skill Eval

Evaluation harness for testing the Mirascope program generation skill.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed
- `MIRASCOPE_API_KEY` environment variable set

## Quick Start

```bash
cd evals/mirascope_skill

# 1. Generate a program and run queries
MIRASCOPE_API_KEY=<your-key> ./skill/run_bootstrap.py \
  --sample samples/invoice_generator/sample_001.yaml \
  --output results/my_run

# 2. Annotate results interactively
./skill/annotate.py results/my_run/bootstrap_results.json

# 3. Run iteration (LOO cross-validation with feedback)
MIRASCOPE_API_KEY=<your-key> ./skill/run_iteration.py \
  --sample samples/invoice_generator/sample_001.yaml \
  --bootstrap results/my_run/bootstrap_results.json \
  --output results/my_run_iteration

# 4. Generate report
./skill/report.py \
  --bootstrap results/my_run/bootstrap_results.json \
  --iteration results/my_run_iteration/iteration_results.json \
  --sample samples/invoice_generator/sample_001.yaml
```

## Scripts

All scripts are self-contained [uv scripts](https://docs.astral.sh/uv/guides/scripts/) with inline dependencies.

| Script | Description |
|--------|-------------|
| `./skill/run_bootstrap.py` | Generate program from SKILL.md + bootstrap prompt, run queries |
| `./skill/run_iteration.py` | LOO cross-validation with feedback-based improvement |
| `./skill/annotate.py` | Interactive annotation of results |
| `./skill/report.py` | Compute and display eval metrics |

## Directory Structure

```
evals/mirascope_skill/
├── skill/
│   ├── SKILL.md           # Instructions for program generation
│   ├── template.py        # Example program template
│   ├── run_bootstrap.py   # Bootstrap eval script
│   ├── run_iteration.py   # Iteration eval script
│   ├── annotate.py        # Interactive annotation
│   └── report.py          # Metrics reporter
├── samples/
│   └── invoice_generator/
│       └── sample_001.yaml  # Eval sample with queries
└── results/                 # Output directory (gitignored)
```

## Eval Flow

1. **Bootstrap**: Generate a program from the skill instructions and a bootstrap prompt
2. **Query Execution**: Run test queries through orchestration → program
3. **Annotation**: Mark results as acceptable/unacceptable with feedback
4. **Iteration**: Improve the program using LOO cross-validation
5. **Report**: Compare bootstrap vs iteration performance

## Sample Format

See `samples/invoice_generator/sample_001.yaml` for the eval sample schema:
- `bootstrap.prompt`: Natural language request for the program
- `queries`: List of test queries with expected outcomes
- Each query has `specificity` (detailed/moderate/vague) and `professionalism` (formal/neutral/casual)
