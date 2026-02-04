"""Random effect selection for YTPPlus."""
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Effect:
    name: str
    video_filter: str
    audio_filter: str


EFFECTS: list[Effect] = [
    Effect(
        name="mirror",
        video_filter="hflip",
        audio_filter="volume=1.0",
    ),
    Effect(
        name="reverse",
        video_filter="reverse",
        audio_filter="areverse",
    ),
    Effect(
        name="speed-up",
        video_filter="setpts=0.5*PTS",
        audio_filter="atempo=2.0",
    ),
    Effect(
        name="slow-down",
        video_filter="setpts=2.0*PTS",
        audio_filter="atempo=0.5",
    ),
    Effect(
        name="chorus",
        video_filter="null",
        audio_filter="chorus=0.7:0.9:55:0.4:0.25:2",
    ),
    Effect(
        name="vibrato",
        video_filter="null",
        audio_filter="vibrato=f=5.0:d=0.5",
    ),
    Effect(
        name="hue-spin",
        video_filter="hue=h=2*PI*t",
        audio_filter="volume=1.0",
    ),
]


def available_effects() -> list[str]:
    return [effect.name for effect in EFFECTS]


def random_effect(rng: random.Random | None = None, allowed: set[str] | None = None) -> Effect:
    generator = rng or random
    if allowed:
        filtered = [effect for effect in EFFECTS if effect.name in allowed]
        if filtered:
            return generator.choice(filtered)
    return generator.choice(EFFECTS)


