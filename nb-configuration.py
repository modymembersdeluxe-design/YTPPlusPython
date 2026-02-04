"""Configuration defaults for YTPPlus.

This mirrors NetBeans-style configuration naming used in the original project.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NbConfiguration:
    app_name: str = "YTPPlus"
    version: str = "1.0"
    author: str = "Ben B. (forked)"
    default_segments: int = 8


CONFIG = NbConfiguration()

