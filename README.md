# YTPPlus v1.0 (Python)

A Python fork of the YTP generator that randomly remixes videos using FFmpeg. It includes a
Tkinter UI plus a CLI entry point for creating nonsensical mashups.

## Requirements

- Python 3.10+
- FFmpeg (`ffmpeg` and `ffprobe` in your `PATH`)

## Quick Start

### UI

```bash
python MainApp.py
```

The UI lets you:

- Choose an input video and output path.
- Toggle effects such as reverse, speed changes, chorus, vibrato, and hue spin.
- Enable random sounds and resource overlays.
- Browse local video/audio/image/GIF sources and add online URLs.

### CLI

```bash
python PythonController.py input.mp4 output.mp4 --segments 12 --effects reverse speed-up --random-sound --overlay
```

## Resource Folders

The UI pre-loads sources from these folders if they exist:

- `resources/images`
- `resources/memes`
- `resources/meme_sounds`
- `resources/sounds`
- `resources/overlay_videos`
- `resources/adverts`
- `resources/errors`
- `resources/spadinner`
- `resources/spadinner_sounds`

You can also add additional sources using the UI browsers.

## Notes

- Effects and overlays are applied per segment with FFmpeg filters.
- “Chaos export” is wired through the UI and CLI for future expansion.
