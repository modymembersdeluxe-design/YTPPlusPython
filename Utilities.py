"""Utility helpers for YTPPlus."""
from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


class YTPError(RuntimeError):
    """Raised when the YTP pipeline fails."""


def run_command(command: list[str]) -> CommandResult:
    """Run a command and capture output."""
    process = subprocess.run(
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return CommandResult(
        command=command,
        returncode=process.returncode,
        stdout=process.stdout,
        stderr=process.stderr,
    )


def ensure_success(result: CommandResult) -> None:
    if result.returncode != 0:
        raise YTPError(
            "Command failed with code {}: {}\n{}".format(
                result.returncode,
                shlex.join(result.command),
                result.stderr.strip(),
            )
        )


def check_ffmpeg() -> None:
    """Ensure ffmpeg and ffprobe are available."""
    for tool in ("ffmpeg", "ffprobe"):
        result = run_command([tool, "-version"])
        if result.returncode != 0:
            raise YTPError(f"{tool} is required but was not found in PATH.")


def ensure_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def list_media_files(folder: str, extensions: set[str]) -> list[str]:
    """Return sorted media files in a folder that match extensions."""
    root = Path(folder)
    if not root.exists():
        return []
    files = [
        str(path)
        for path in root.iterdir()
        if path.is_file() and path.suffix.lower() in extensions
    ]
    return sorted(files)


