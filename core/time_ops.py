# core/time_ops.py
from typing import Any

def to_seconds(time_obj: Any) -> float:
    """pysrt time → seconds."""
    return (
        time_obj.hours * 3600
        + time_obj.minutes * 60
        + time_obj.seconds
        + time_obj.milliseconds / 1000.0
    )

def overlap(a1: float, b1: float, a2: float, b2: float) -> float:
    """Length of intersection between [a1,b1] and [a2,b2]."""
    return max(0.0, min(b1, b2) - max(a1, a2))
