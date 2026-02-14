# Scheduling Agent Eval

Evaluates an AI scheduling agent's ability to manage calendar operations through tool use.

## Overview

This eval tests core scheduling competencies:
- **Availability checking**: Querying free time slots
- **Booking**: Creating new appointments with validation
- **Conflict handling**: Detecting and suggesting alternatives for conflicts
- **Rescheduling**: Moving existing appointments
- **Cancellation**: Removing appointments

## Structure

```
scheduling_agent/
├── README.md
├── skill/
│   └── SKILL.md          # Agent implementation guide
├── samples/
│   ├── simple_booking/   # Basic happy-path booking
│   ├── availability_check/  # Querying available times
│   ├── conflict_handling/   # Double-booking scenarios
│   ├── reschedule/          # Moving appointments
│   └── cancellation/        # Removing appointments
└── results/              # Eval run outputs
```

## Sample Format

Each sample defines:
- **context**: Date context and initial calendar state
- **queries**: User messages with expected behavior
- **validation**: Automated checks for correctness

## Evaluation Criteria

1. **Tool Selection**: Did the agent call the right tools?
2. **Argument Accuracy**: Were tool arguments correct?
3. **Sequence Logic**: Did tools execute in sensible order?
4. **Error Handling**: Did the agent handle conflicts gracefully?
5. **User Communication**: Was the response clear and helpful?

## Running Evals

```bash
# Bootstrap agent from skill
./skill/run_bootstrap.py --sample samples/simple_booking/sample_001.yaml

# Run single query
./skill/run_query.py --input "Book John at 2pm tomorrow"

# Full eval suite
./skill/run_eval.py --samples samples/
```
