#!/usr/bin/env -S uv run --python 3.13
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mirascope[all]>=2.0",
#     "pydantic>=2.0",
#     "pyyaml>=6.0",
# ]
# ///
"""Run scheduling agent eval against samples."""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel
from mirascope import llm
from mirascope.llm import UserMessage, SystemMessage, Message, Text


# ============================================================================
# Models
# ============================================================================

class TimeSlot(BaseModel):
    start: datetime
    end: datetime
    available: bool


class Appointment(BaseModel):
    id: str
    client_name: str
    client_email: str
    start: datetime
    end: datetime
    notes: str | None = None


# Calendar state
_calendar: dict[str, Appointment] = {}


def reset_calendar(appointments: list[dict] | None = None):
    """Reset calendar state for testing."""
    global _calendar
    _calendar = {}
    for apt in appointments or []:
        _calendar[apt["id"]] = Appointment(
            id=apt["id"],
            client_name=apt["client_name"],
            client_email=apt["client_email"],
            start=datetime.fromisoformat(apt["start"]),
            end=datetime.fromisoformat(apt["end"]),
            notes=apt.get("notes"),
        )


# ============================================================================
# Tools
# ============================================================================

@llm.tool
def check_availability(date: str, start_hour: int = 9, end_hour: int = 17) -> list[dict]:
    """Check available time slots for a given date.
    
    Args:
        date: Date to check in YYYY-MM-DD format
        start_hour: Start of business hours (default 9)
        end_hour: End of business hours (default 17)
    
    Returns:
        List of 30-minute time slots with availability status
    """
    target = datetime.fromisoformat(date)
    slots = []
    current = target.replace(hour=start_hour, minute=0)
    end = target.replace(hour=end_hour, minute=0)
    
    while current < end:
        slot_end = current + timedelta(minutes=30)
        is_available = not any(
            apt.start < slot_end and apt.end > current
            for apt in _calendar.values()
        )
        slots.append({
            "start": current.isoformat(),
            "end": slot_end.isoformat(),
            "available": is_available,
        })
        current = slot_end
    
    return slots


@llm.tool
def book_appointment(
    client_name: str,
    client_email: str,
    start_time: str,
    duration_minutes: int = 30,
    notes: str | None = None,
) -> dict:
    """Book a new appointment.
    
    Args:
        client_name: Name of the client
        client_email: Client's email address
        start_time: Start time in ISO format (YYYY-MM-DDTHH:MM)
        duration_minutes: Duration in minutes (default 30)
        notes: Optional notes for the appointment
    
    Returns:
        The created appointment
    """
    start = datetime.fromisoformat(start_time)
    end = start + timedelta(minutes=duration_minutes)
    
    for apt in _calendar.values():
        if apt.start < end and apt.end > start:
            raise ValueError(f"Time slot conflicts with existing appointment: {apt.id}")
    
    apt_id = f"apt_{len(_calendar) + 1:04d}"
    appointment = Appointment(
        id=apt_id,
        client_name=client_name,
        client_email=client_email,
        start=start,
        end=end,
        notes=notes,
    )
    _calendar[apt_id] = appointment
    return appointment.model_dump(mode="json")


@llm.tool
def send_confirmation(appointment_id: str) -> str:
    """Send a confirmation email for an appointment."""
    if appointment_id not in _calendar:
        raise ValueError(f"Appointment not found: {appointment_id}")
    apt = _calendar[appointment_id]
    return f"Confirmation sent to {apt.client_email} for {apt.start.strftime('%B %d at %I:%M %p')}"


@llm.tool
def reschedule_appointment(appointment_id: str, new_start_time: str) -> dict:
    """Reschedule an existing appointment."""
    if appointment_id not in _calendar:
        raise ValueError(f"Appointment not found: {appointment_id}")
    
    old_apt = _calendar[appointment_id]
    duration = old_apt.end - old_apt.start
    new_start = datetime.fromisoformat(new_start_time)
    new_end = new_start + duration
    
    for apt_id, apt in _calendar.items():
        if apt_id != appointment_id and apt.start < new_end and apt.end > new_start:
            raise ValueError(f"New time conflicts with: {apt_id}")
    
    old_apt.start = new_start
    old_apt.end = new_end
    return old_apt.model_dump(mode="json")


@llm.tool
def cancel_appointment(appointment_id: str) -> str:
    """Cancel an appointment."""
    if appointment_id not in _calendar:
        raise ValueError(f"Appointment not found: {appointment_id}")
    apt = _calendar.pop(appointment_id)
    return f"Cancelled appointment with {apt.client_name} on {apt.start.strftime('%B %d at %I:%M %p')}"


@llm.tool
def list_appointments(date: str | None = None) -> list[dict]:
    """List appointments, optionally filtered by date."""
    appointments = list(_calendar.values())
    if date:
        target = datetime.fromisoformat(date).date()
        appointments = [apt for apt in appointments if apt.start.date() == target]
    return [apt.model_dump(mode="json") for apt in sorted(appointments, key=lambda a: a.start)]


# ============================================================================
# Agent
# ============================================================================

TOOLS = [
    check_availability,
    book_appointment,
    send_confirmation,
    reschedule_appointment,
    cancel_appointment,
    list_appointments,
]

SYSTEM_PROMPT = """You are a scheduling assistant. You help users manage their calendar by:
- Checking availability
- Booking appointments  
- Sending confirmations
- Rescheduling or cancelling as needed

Always confirm details before booking. When booking, always send a confirmation.
If a requested time isn't available, suggest alternatives.

Today's date is {today}.
"""


@llm.call(model="anthropic/claude-sonnet-4-20250514", tools=TOOLS)
def scheduling_agent(user_message: str, history: list[Message], today: str) -> list[Message]:
    messages: list[Message] = [
        SystemMessage(content=Text(text=SYSTEM_PROMPT.format(today=today)))
    ]
    messages.extend(history)
    if user_message:
        messages.append(UserMessage(content=[Text(text=user_message)]))
    return messages


def run_agent(user_message: str, today: str) -> tuple[str, list[dict]]:
    """Run agent to completion, return response and tool call log."""
    tool_calls_log: list[dict] = []
    
    response = scheduling_agent(user_message, [], today)
    
    while response.tool_calls:
        # Log tool calls
        for tc in response.tool_calls:
            import json
            tool_calls_log.append({"tool": tc.name, "args": json.loads(tc.args)})
        
        # Execute tools and resume
        results = response.execute_tools()
        
        # Log results
        for i, result in enumerate(results):
            if result.error:
                tool_calls_log[len(tool_calls_log) - len(results) + i]["error"] = result.error
            else:
                tool_calls_log[len(tool_calls_log) - len(results) + i]["result"] = result.result
        
        response = response.resume(results)
    
    # Extract text content - response.content is a list of Text objects
    text_parts = [part.text for part in response.content if hasattr(part, 'text')]
    content = ' '.join(text_parts)
    return content, tool_calls_log


# ============================================================================
# Eval Runner
# ============================================================================

def run_sample(sample_path: Path) -> dict:
    """Run a single sample and return results."""
    with open(sample_path) as f:
        sample = yaml.safe_load(f)
    
    # Setup context
    today = sample.get("context", {}).get("today", datetime.now().strftime("%Y-%m-%d"))
    calendar_state = sample.get("context", {}).get("calendar_state", [])
    reset_calendar(calendar_state)
    
    results = []
    for query in sample.get("queries", []):
        user_input = query["input"]
        response, tool_calls = run_agent(user_input, today)
        
        # Check validations
        validations = sample.get("validation", [])
        passed = []
        failed = []
        
        for v in validations:
            vtype = v.get("type")
            if vtype == "tool_called":
                tool_name = v.get("tool")
                matching = [tc for tc in tool_calls if tc["tool"] == tool_name]
                if matching:
                    # Check args if specified
                    args_contain = v.get("args_contain", {})
                    if args_contain:
                        match_found = any(
                            all(tc["args"].get(k) == val for k, val in args_contain.items())
                            for tc in matching
                        )
                        if match_found:
                            passed.append(f"tool_called:{tool_name} with args")
                        else:
                            failed.append(f"tool_called:{tool_name} missing expected args {args_contain}")
                    else:
                        passed.append(f"tool_called:{tool_name}")
                else:
                    failed.append(f"tool_called:{tool_name} (not called)")
            
            elif vtype == "tool_not_called":
                tool_name = v.get("tool")
                matching = [tc for tc in tool_calls if tc["tool"] == tool_name]
                if not matching:
                    passed.append(f"tool_not_called:{tool_name}")
                else:
                    failed.append(f"tool_not_called:{tool_name} (was called)")
            
            elif vtype == "response_contains":
                patterns = v.get("patterns", [])
                response_lower = response.lower()
                for pattern in patterns:
                    if pattern.lower() in response_lower:
                        passed.append(f"response_contains:{pattern}")
                    else:
                        failed.append(f"response_contains:{pattern}")
        
        results.append({
            "input": user_input,
            "response": response,
            "tool_calls": tool_calls,
            "passed": passed,
            "failed": failed,
            "success": len(failed) == 0,
        })
    
    return {
        "sample": sample_path.name,
        "name": sample.get("name", "unnamed"),
        "results": results,
        "all_passed": all(r["success"] for r in results),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=Path, help="Single sample to run")
    parser.add_argument("--samples-dir", type=Path, help="Directory of samples")
    parser.add_argument("--output", type=Path, help="Output JSON file")
    args = parser.parse_args()
    
    samples = []
    if args.sample:
        samples = [args.sample]
    elif args.samples_dir:
        samples = list(args.samples_dir.rglob("*.yaml"))
    else:
        # Default: find samples relative to this script
        script_dir = Path(__file__).parent.parent
        samples_dir = script_dir / "samples"
        if samples_dir.exists():
            samples = list(samples_dir.rglob("*.yaml"))
    
    if not samples:
        print("No samples found")
        sys.exit(1)
    
    print(f"Running {len(samples)} sample(s)...\n")
    
    all_results = []
    passed = 0
    failed = 0
    
    for sample_path in sorted(samples):
        print(f"▶ {sample_path.parent.name}/{sample_path.name}")
        result = run_sample(sample_path)
        all_results.append(result)
        
        for r in result["results"]:
            if r["success"]:
                passed += 1
                print(f"  ✓ {r['input'][:50]}...")
            else:
                failed += 1
                print(f"  ✗ {r['input'][:50]}...")
                for f in r["failed"]:
                    print(f"    - {f}")
        print()
    
    total = passed + failed
    print(f"Results: {passed}/{total} ({100*passed/total:.0f}%)")
    
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"Wrote results to {args.output}")
    
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
