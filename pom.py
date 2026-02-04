"""Metadata mirroring a Java pom for documentation purposes."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PomMetadata:
    group_id: str = "com.example.ytpplus"
    artifact_id: str = "ytpplus"
    version: str = "1.0"
    description: str = "Random nonsensical YTP video remix generator"


POM = PomMetadata()

