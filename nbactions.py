"""Action helpers inspired by NetBeans build actions."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Action:
    name: str
    description: str


ACTIONS = [
    Action(name="run-cli", description="Run the YTPPlus CLI generator"),
    Action(name="run-ui", description="Launch the Tkinter UI"),
]


def list_actions() -> list[Action]:
    return ACTIONS.copy()


