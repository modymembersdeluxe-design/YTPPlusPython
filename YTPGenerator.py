"""Core generation logic for YTPPlus."""
from __future__ import annotations

import os
import random
import tempfile
from dataclasses import dataclass

from EffectsFactory import random_effect
from TimeStamp import TimeStamp
from Utilities import YTPError, check_ffmpeg, ensure_directory, ensure_success, run_command


@dataclass
class GenerationConfig:
    segment_count: int = 8
    min_duration: float = 0.4
    max_duration: float = 1.4
    seed: int | None = None
    enabled_effects: set[str] | None = None
    random_sound: bool = False
    overlay_enabled: bool = False
    chaos_export: bool = False
    sound_files: list[str] | None = None
    overlay_images: list[str] | None = None
    overlay_videos: list[str] | None = None


class YTPGenerator:
    def __init__(self, config: GenerationConfig | None = None) -> None:
        self.config = config or GenerationConfig()
        self.rng = random.Random(self.config.seed)

    def _probe_duration(self, input_path: str) -> float:
        result = run_command(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "format=duration",
                "-of",
                "default=nokey=1:noprint_wrappers=1",
                input_path,
            ]
        )
        ensure_success(result)
        try:
            return float(result.stdout.strip())
        except ValueError as exc:
            raise YTPError("Unable to parse video duration.") from exc

    def _random_segment(self, duration: float) -> TimeStamp:
        segment_duration = self.rng.uniform(
            self.config.min_duration,
            self.config.max_duration,
        )
        max_start = max(0.0, duration - segment_duration)
        start = self.rng.uniform(0.0, max_start)
        return TimeStamp(start=start, end=start + segment_duration)

    def _choose_overlay(self) -> tuple[str | None, bool]:
        if not self.config.overlay_enabled:
            return (None, False)
        choices: list[tuple[str, bool]] = []
        for image in self.config.overlay_images or []:
            choices.append((image, True))
        for video in self.config.overlay_videos or []:
            choices.append((video, False))
        if not choices:
            return (None, False)
        return self.rng.choice(choices)

    def _choose_audio(self) -> str | None:
        if self.config.random_sound and self.config.sound_files:
            return self.rng.choice(self.config.sound_files)
        return None

    def _render_segment(
        self,
        input_path: str,
        output_path: str,
        segment: TimeStamp,
    ) -> None:
        start, seg_duration = segment.to_ffmpeg()
        effect = random_effect(self.rng, self.config.enabled_effects)
        overlay_path, is_image = self._choose_overlay()
        audio_path = self._choose_audio()

        command = [
            "ffmpeg",
            "-y",
            "-ss",
            start,
            "-t",
            seg_duration,
            "-i",
            input_path,
        ]

        filter_complex_parts: list[str] = []
        video_label = "[v0]"
        audio_label = "[a0]"

        if overlay_path:
            if is_image:
                command.extend(["-loop", "1", "-i", overlay_path])
            else:
                command.extend(["-i", overlay_path])
            filter_complex_parts.append(
                f"[0:v]{effect.video_filter}[vbase]"
            )
            filter_complex_parts.append(
                "[vbase][1:v]overlay=10:10:format=auto[v0]"
            )
        else:
            filter_complex_parts.append(f"[0:v]{effect.video_filter}[v0]")

        if audio_path:
            command.extend(["-i", audio_path])
            filter_complex_parts.append(f"[2:a]{effect.audio_filter}[a0]")
        else:
            filter_complex_parts.append(f"[0:a]{effect.audio_filter}[a0]")

        command.extend(
            [
                "-filter_complex",
                ";".join(filter_complex_parts),
                "-map",
                video_label,
                "-map",
                audio_label,
                "-shortest",
                "-preset",
                "veryfast",
                "-movflags",
                "+faststart",
                output_path,
            ]
        )

        result = run_command(command)
        ensure_success(result)

    def _concat_segments(self, segments: list[str], output_path: str) -> None:
        concat_list = "\n".join(f"file '{segment}'" for segment in segments)
        list_path = os.path.join(os.path.dirname(output_path), "concat.txt")
        with open(list_path, "w", encoding="utf-8") as handle:
            handle.write(concat_list)
        result = run_command(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                list_path,
                "-c",
                "copy",
                output_path,
            ]
        )
        ensure_success(result)

    def generate(self, input_path: str, output_path: str) -> None:
        check_ffmpeg()
        if not os.path.exists(input_path):
            raise YTPError(f"Input file not found: {input_path}")

        ensure_directory(os.path.dirname(output_path) or ".")
        duration = self._probe_duration(input_path)

        with tempfile.TemporaryDirectory(prefix="ytpplus_") as working:
            segments: list[str] = []
            for index in range(self.config.segment_count):
                segment = self._random_segment(duration)
                segment_path = os.path.join(working, f"segment_{index}.mp4")
                self._render_segment(input_path, segment_path, segment)
                segments.append(segment_path)

            self._concat_segments(segments, output_path)


