# Scheduling Agent Skill

Build AI agents that manage calendar scheduling with tool-based interactions.

## Overview

A scheduling agent uses tools to:
- Check calendar availability
- Book appointments
- Send confirmations
- Handle rescheduling and cancellations

## Dependencies

```toml
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mirascope[all]>=2.0",
#     "pydantic>=2.0",
# ]
# ///
```

## Tool Definitions

Define tools as typed functions with clear docstrings:

```python
from datetime import datetime, timedelta
from pydantic import BaseModel
from mirascope import llm


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


# Simulated calendar state (in production, connect to real calendar API)
_calendar: dict[str, Appointment] = {}


def check_availability(date: str, start_hour: int = 9, end_hour: int = 17) -> list[TimeSlot]:
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
        # Check if any appointment overlaps this slot
        is_available = not any(
            apt.start < slot_end and apt.end > current
            for apt in _calendar.values()
        )
        slots.append(TimeSlot(start=current, end=slot_end, available=is_available))
        current = slot_end
    
    return slots


def book_appointment(
    client_name: str,
    client_email: str,
    start_time: str,
    duration_minutes: int = 30,
    notes: str | None = None,
) -> Appointment:
    """Book a new appointment.
    
    Args:
        client_name: Name of the client
        client_email: Client's email address
        start_time: Start time in ISO format (YYYY-MM-DDTHH:MM)
        duration_minutes: Duration in minutes (default 30)
        notes: Optional notes for the appointment
    
    Returns:
        The created appointment
    
    Raises:
        ValueError: If the slot is not available
    """
    start = datetime.fromisoformat(start_time)
    end = start + timedelta(minutes=duration_minutes)
    
    # Check for conflicts
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
    return appointment


def send_confirmation(appointment_id: str) -> str:
    """Send a confirmation email for an appointment.
    
    Args:
        appointment_id: ID of the appointment to confirm
    
    Returns:
        Confirmation message
    """
    if appointment_id not in _calendar:
        raise ValueError(f"Appointment not found: {appointment_id}")
    
    apt = _calendar[appointment_id]
    # In production, actually send email
    return f"Confirmation sent to {apt.client_email} for {apt.start.strftime('%B %d at %I:%M %p')}"


def reschedule_appointment(appointment_id: str, new_start_time: str) -> Appointment:
    """Reschedule an existing appointment.
    
    Args:
        appointment_id: ID of the appointment to reschedule
        new_start_time: New start time in ISO format
    
    Returns:
        Updated appointment
    
    Raises:
        ValueError: If appointment not found or new slot unavailable
    """
    if appointment_id not in _calendar:
        raise ValueError(f"Appointment not found: {appointment_id}")
    
    old_apt = _calendar[appointment_id]
    duration = old_apt.end - old_apt.start
    new_start = datetime.fromisoformat(new_start_time)
    new_end = new_start + duration
    
    # Check for conflicts (excluding this appointment)
    for apt_id, apt in _calendar.items():
        if apt_id != appointment_id and apt.start < new_end and apt.end > new_start:
            raise ValueError(f"New time conflicts with: {apt_id}")
    
    old_apt.start = new_start
    old_apt.end = new_end
    return old_apt


def cancel_appointment(appointment_id: str) -> str:
    """Cancel an appointment.
    
    Args:
        appointment_id: ID of the appointment to cancel
    
    Returns:
        Cancellation confirmation
    """
    if appointment_id not in _calendar:
        raise ValueError(f"Appointment not found: {appointment_id}")
    
    apt = _calendar.pop(appointment_id)
    return f"Cancelled appointment with {apt.client_name} on {apt.start.strftime('%B %d at %I:%M %p')}"


def list_appointments(date: str | None = None) -> list[Appointment]:
    """List appointments, optionally filtered by date.
    
    Args:
        date: Optional date filter in YYYY-MM-DD format
    
    Returns:
        List of appointments
    """
    appointments = list(_calendar.values())
    if date:
        target = datetime.fromisoformat(date).date()
        appointments = [apt for apt in appointments if apt.start.date() == target]
    return sorted(appointments, key=lambda a: a.start)
```

## Agent Implementation

```python
from mirascope import llm, BaseMessageParam


SYSTEM_PROMPT = """You are a scheduling assistant. You help users manage their calendar by:
- Checking availability
- Booking appointments  
- Sending confirmations
- Rescheduling or cancelling as needed

Always confirm details before booking. When booking, always send a confirmation.
If a requested time isn't available, suggest alternatives.

Today's date is {today}.
"""


@llm.call(
    provider="anthropic",
    model="claude-sonnet-4-20250514",
    tools=[
        check_availability,
        book_appointment,
        send_confirmation,
        reschedule_appointment,
        cancel_appointment,
        list_appointments,
    ],
)
def scheduling_agent(
    user_message: str,
    history: list[BaseMessageParam] | None = None,
) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    messages = history or []
    messages.append({"role": "user", "content": user_message})
    return {"system": SYSTEM_PROMPT.format(today=today), "messages": messages}
```

## Agentic Loop

Handle multi-turn tool execution:

```python
def run_agent(user_message: str, history: list[BaseMessageParam] | None = None) -> str:
    """Run the scheduling agent to completion."""
    history = history or []
    response = scheduling_agent(user_message, history)
    
    while response.tool_calls:
        # Execute all tool calls
        tool_results = []
        for tool_call in response.tool_calls:
            try:
                result = tool_call.call()
                tool_results.append({"tool": tool_call.name, "result": result})
            except Exception as e:
                tool_results.append({"tool": tool_call.name, "error": str(e)})
        
        # Continue conversation with tool results
        history = response.history + [
            {"role": "assistant", "tool_calls": response.tool_calls},
            {"role": "tool", "content": tool_results},
        ]
        response = scheduling_agent("", history)
    
    return response.content
```

## Robustness Patterns

### Error Handling

Tools should raise clear exceptions that the agent can interpret:

```python
def book_appointment(...) -> Appointment:
    # Validate inputs
    try:
        start = datetime.fromisoformat(start_time)
    except ValueError:
        raise ValueError(f"Invalid datetime format: {start_time}. Use YYYY-MM-DDTHH:MM")
    
    # Check conflicts with helpful message
    for apt in _calendar.values():
        if apt.start < end and apt.end > start:
            raise ValueError(
                f"Slot unavailable. Conflicts with {apt.client_name}'s appointment "
                f"from {apt.start.strftime('%I:%M %p')} to {apt.end.strftime('%I:%M %p')}"
            )
```

### State Injection for Testing

For deterministic tests, inject calendar state:

```python
def reset_calendar(appointments: list[Appointment] | None = None):
    """Reset calendar state for testing."""
    global _calendar
    _calendar = {apt.id: apt for apt in (appointments or [])}
```

## Evaluation Criteria

A scheduling agent should:

1. **Understand intent**: Parse natural language requests correctly
2. **Check before booking**: Always verify availability first
3. **Handle conflicts**: Suggest alternatives when slots are taken
4. **Confirm actions**: Send confirmations after successful bookings
5. **Manage errors gracefully**: Clear messages when things fail
6. **Multi-step execution**: Chain tools appropriately (check → book → confirm)
