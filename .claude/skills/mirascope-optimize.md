# Mirascope Optimize Skill

Iterate on Mirascope AI agents until they meet quality thresholds using an AI engineering loop.

## Overview

This skill helps you systematically improve Mirascope agents by running evaluations, analyzing results in Mirascope Cloud, and iterating on prompts/tools based on failure patterns.

## Prerequisites

1. **Mirascope Cloud Setup**: Ensure `MIRASCOPE_API_KEY` is set in your environment
2. **Agent Instrumented**: The target agent should use `@ops.version` for tracing
3. **Test Data Available**: Test cases covering expected patterns and edge cases

## Workflow

### Phase 1: Setup

```python
# Configure ops at startup
from mirascope import ops
ops.configure()
```

### Phase 2: Run Evaluation

```python
from mirascope.cli.migrate.eval_runner import run_quick_evaluation, print_report

# Run on a subset of test cases
report = run_quick_evaluation(n_cases=10)
print_report(report)
```

### Phase 3: Analyze Results

After running evaluation:

1. **Review metrics in terminal**:
   - Overall score (target: 85%+)
   - Correctness, Completeness, Quality, Safety breakdowns
   - Failed patterns and common issues

2. **Analyze traces in Mirascope Cloud**:
   - Navigate to the project dashboard
   - Filter by `@ops.version` name (e.g., "migration_agent")
   - Review failed cases to identify patterns

### Phase 4: Iterate

Based on analysis, modify:

1. **Prompts**: Update system prompts or instructions
2. **Tools**: Fix or enhance tool implementations
3. **Agent Logic**: Adjust control flow or error handling

Changes are automatically tracked via `@ops.version` hashes.

### Phase 5: Re-evaluate

Run evaluation again to measure improvement:

```python
# Run same test cases after changes
report = run_quick_evaluation(n_cases=10)
print_report(report)

# Compare version-over-version in Mirascope Cloud
```

## Evaluation Criteria

The evaluation framework scores migrations on:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Correctness | 40% | Syntactically valid Python, will it run? |
| Completeness | 30% | All v0/v1 patterns migrated to v2? |
| Quality | 20% | Idiomatic v2 code (uses @llm.call, etc.)? |
| Safety | 10% | Comments/docstrings preserved, no unintended changes? |

## Key Modules

| Module | Purpose |
|--------|---------|
| `mirascope.cli.migrate.agent` | The migration agent (versioned with @ops.version) |
| `mirascope.cli.migrate.evaluation` | LLM judge + programmatic verification |
| `mirascope.cli.migrate.eval_runner` | Run evaluations and aggregate results |
| `mirascope.cli.migrate.test_data` | Test case loader (synthetic + examples) |
| `mirascope.cli.migrate.patterns` | Pattern detection for v0/v1 code |

## Example Session

```bash
# 1. Initial evaluation
cd python
python -c "
from mirascope.cli.migrate.eval_runner import run_quick_evaluation, print_report
report = run_quick_evaluation(n_cases=5, difficulty='simple')
print_report(report)
"

# 2. Review results in Mirascope Cloud
# Look for failed patterns and common issues

# 3. Make changes to prompts.py or tools.py based on analysis

# 4. Re-run evaluation to measure improvement
python -c "
from mirascope.cli.migrate.eval_runner import run_quick_evaluation, print_report
report = run_quick_evaluation(n_cases=5, difficulty='simple')
print_report(report)
"
```

## Tips

- **Start simple**: Begin with "simple" difficulty cases before moving to "complex"
- **Version tracking**: All changes are tracked via `@ops.version` hashes
- **Iterate incrementally**: Fix one pattern category at a time
- **Align the judge**: Review LLM judge output and adjust if needed
- **Expand gradually**: Once scores are good, add more test cases

## Commands

```bash
# Run migration CLI
uvx mirascope migrate --path /path/to/project

# Run with specific model
uvx mirascope migrate --path /path/to/project --model anthropic/claude-sonnet-4-5

# Dry run (no changes)
uvx mirascope migrate --path /path/to/project --dry-run
```
