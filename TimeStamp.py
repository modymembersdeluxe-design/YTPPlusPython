"""Timestamp helpers for YTPPlus."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeStamp:
    start: float
    end: float

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)

    def clamp(self, max_duration: float) -> "TimeStamp":
        start = max(0.0, min(self.start, max_duration))
        end = max(0.0, min(self.end, max_duration))
        if end < start:
            end = start
        return TimeStamp(start=start, end=end)

    def to_ffmpeg(self) -> tuple[str, str]:
        return (f"{self.start:.3f}", f"{self.duration:.3f}")


