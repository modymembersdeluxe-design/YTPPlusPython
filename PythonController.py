"""Controller entry points for CLI and UI."""
from __future__ import annotations

import argparse
from dataclasses import dataclass

from EffectsFactory import available_effects
from YTPGenerator import GenerationConfig, YTPGenerator


@dataclass
class ControllerConfig:
    input_path: str
    output_path: str
    segment_count: int = 8
    seed: str | None = None
    enabled_effects: set[str] | None = None
    random_sound: bool = False
    overlay_enabled: bool = False
    chaos_export: bool = False
    sound_files: list[str] | None = None
    overlay_images: list[str] | None = None
    overlay_videos: list[str] | None = None


class YTPController:
    def generate(self, config: ControllerConfig) -> None:
        seed_value = int(config.seed) if config.seed is not None else None
        generator = YTPGenerator(
            GenerationConfig(
                segment_count=config.segment_count,
                seed=seed_value,
                enabled_effects=config.enabled_effects,
                random_sound=config.random_sound,
                overlay_enabled=config.overlay_enabled,
                chaos_export=config.chaos_export,
                sound_files=config.sound_files,
                overlay_images=config.overlay_images,
                overlay_videos=config.overlay_videos,
            )
        )
        generator.generate(config.input_path, config.output_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="YTPPlus v1.0")
    parser.add_argument("input", help="Input video file")
    parser.add_argument("output", help="Output video file")
    parser.add_argument("--segments", type=int, default=8, help="Number of segments")
    parser.add_argument("--seed", help="Random seed (optional)")
    parser.add_argument(
        "--effects",
        nargs="*",
        default=None,
        choices=available_effects(),
        help="Enable specific effects by name",
    )
    parser.add_argument("--random-sound", action="store_true", help="Use random sounds")
    parser.add_argument("--overlay", action="store_true", help="Enable overlays")
    parser.add_argument("--chaos", action="store_true", help="Enable chaos export")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    controller = YTPController()
    controller.generate(
        ControllerConfig(
            input_path=args.input,
            output_path=args.output,
            segment_count=args.segments,
            seed=args.seed,
            enabled_effects=set(args.effects) if args.effects else None,
            random_sound=args.random_sound,
            overlay_enabled=args.overlay,
            chaos_export=args.chaos,
        )
    )


if __name__ == "__main__":
    main()

