"""Utility functions for wandb_logged_chain."""
import datetime


def get_time_in_ms() -> int:
    """Returns current time in milliseconds."""
    return round(datetime.datetime.now().timestamp() * 1000)
