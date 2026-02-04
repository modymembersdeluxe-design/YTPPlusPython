"""Tkinter UI for YTPPlus."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

from EffectsFactory import available_effects
from PythonController import ControllerConfig, YTPController
from Utilities import list_media_files


VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}

RESOURCE_FOLDERS = {
    "images": "resources/images",
    "memes": "resources/memes",
    "meme_sounds": "resources/meme_sounds",
    "sounds": "resources/sounds",
    "overlay_videos": "resources/overlay_videos",
    "adverts": "resources/adverts",
    "errors": "resources/errors",
    "spadinner": "resources/spadinner",
    "spadinner_sounds": "resources/spadinner_sounds",
}


class MainApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("YTPPlus v1.0")
        self.geometry("860x720")
        self._controller = YTPController()

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.segment_count = tk.IntVar(value=8)
        self.seed_value = tk.StringVar()
        self.random_sound = tk.BooleanVar(value=False)
        self.overlay_enabled = tk.BooleanVar(value=False)
        self.chaos_export = tk.BooleanVar(value=False)

        self.effect_vars: dict[str, tk.BooleanVar] = {
            name: tk.BooleanVar(value=True) for name in available_effects()
        }

        self.video_sources: list[str] = []
        self.audio_sources: list[str] = []
        self.image_sources: list[str] = []
        self.url_sources: list[str] = []

        self._build_layout()
        self._load_resource_defaults()

    def _build_layout(self) -> None:
        header = tk.Frame(self)
        header.pack(fill="x", padx=12, pady=8)
        tk.Label(header, text="Input video").grid(row=0, column=0, sticky="w")
        tk.Entry(header, textvariable=self.input_path, width=70).grid(row=0, column=1, sticky="w")
        tk.Button(header, text="Browse", command=self._pick_input).grid(row=0, column=2, padx=6)

        tk.Label(header, text="Output video").grid(row=1, column=0, sticky="w", pady=(8, 0))
        tk.Entry(header, textvariable=self.output_path, width=70).grid(row=1, column=1, sticky="w", pady=(8, 0))
        tk.Button(header, text="Browse", command=self._pick_output).grid(row=1, column=2, padx=6, pady=(8, 0))

        options = tk.LabelFrame(self, text="Generation Options")
        options.pack(fill="x", padx=12, pady=10)
        tk.Label(options, text="Segments").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        tk.Spinbox(options, from_=2, to=40, textvariable=self.segment_count, width=6).grid(
            row=0, column=1, sticky="w", padx=8, pady=4
        )
        tk.Label(options, text="Seed (optional)").grid(row=0, column=2, sticky="w", padx=8, pady=4)
        tk.Entry(options, textvariable=self.seed_value, width=16).grid(
            row=0, column=3, sticky="w", padx=8, pady=4
        )

        tk.Checkbutton(options, text="Random sound", variable=self.random_sound).grid(
            row=1, column=0, sticky="w", padx=8, pady=4
        )
        tk.Checkbutton(options, text="Overlay resources", variable=self.overlay_enabled).grid(
            row=1, column=1, sticky="w", padx=8, pady=4
        )
        tk.Checkbutton(options, text="Chaos export", variable=self.chaos_export).grid(
            row=1, column=2, sticky="w", padx=8, pady=4
        )

        effects = tk.LabelFrame(self, text="Toggleable Effects")
        effects.pack(fill="x", padx=12, pady=10)
        for index, name in enumerate(sorted(self.effect_vars)):
            row = index // 4
            column = index % 4
            tk.Checkbutton(effects, text=name, variable=self.effect_vars[name]).grid(
                row=row, column=column, sticky="w", padx=8, pady=4
            )

        sources = tk.LabelFrame(self, text="Source Browsers")
        sources.pack(fill="both", expand=True, padx=12, pady=10)

        self.video_list = self._build_source_list(
            sources,
            "Video Sources",
            0,
            self._add_video_source,
            self._remove_video_source,
        )
        self.audio_list = self._build_source_list(
            sources,
            "Audio Sources",
            1,
            self._add_audio_source,
            self._remove_audio_source,
        )
        self.image_list = self._build_source_list(
            sources,
            "Image/GIF Sources",
            2,
            self._add_image_source,
            self._remove_image_source,
        )
        self.url_list = self._build_source_list(
            sources,
            "Online URLs",
            3,
            self._add_url_source,
            self._remove_url_source,
            url_entry=True,
        )

        tk.Button(self, text="Generate", command=self._run).pack(pady=10)

    def _build_source_list(
        self,
        parent: tk.Widget,
        title: str,
        column: int,
        add_command,
        remove_command,
        url_entry: bool = False,
    ) -> tk.Listbox:
        frame = tk.Frame(parent)
        frame.grid(row=0, column=column, sticky="n", padx=6)
        tk.Label(frame, text=title).pack(anchor="w")
        listbox = tk.Listbox(frame, width=24, height=12)
        listbox.pack()
        if url_entry:
            entry = tk.Entry(frame, width=24)
            entry.pack(pady=2)
            entry.bind(
                "<Return>",
                lambda _event, e=entry: add_command(entry_widget=e),
            )
            add_button = tk.Button(frame, text="Add", command=lambda: add_command(entry_widget=entry))
        else:
            add_button = tk.Button(frame, text="Add", command=add_command)
        add_button.pack(fill="x", pady=(4, 2))
        tk.Button(frame, text="Remove", command=remove_command).pack(fill="x")
        return listbox

    def _pick_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Select input video",
            filetypes=[("Video Files", "*.mp4 *.mov *.mkv *.avi *.webm")],
        )
        if path:
            self.input_path.set(path)

    def _pick_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save output video",
            defaultextension=".mp4",
            filetypes=[("MP4 Video", "*.mp4")],
        )
        if path:
            self.output_path.set(path)

    def _load_resource_defaults(self) -> None:
        video_dirs = [
            RESOURCE_FOLDERS["memes"],
            RESOURCE_FOLDERS["overlay_videos"],
            RESOURCE_FOLDERS["adverts"],
            RESOURCE_FOLDERS["errors"],
            RESOURCE_FOLDERS["spadinner"],
        ]
        audio_dirs = [
            RESOURCE_FOLDERS["meme_sounds"],
            RESOURCE_FOLDERS["sounds"],
            RESOURCE_FOLDERS["spadinner_sounds"],
        ]
        image_dirs = [RESOURCE_FOLDERS["images"]]

        for folder in video_dirs:
            self.video_sources.extend(list_media_files(folder, VIDEO_EXTS))
        for folder in audio_dirs:
            self.audio_sources.extend(list_media_files(folder, AUDIO_EXTS))
        for folder in image_dirs:
            self.image_sources.extend(list_media_files(folder, IMAGE_EXTS))

        self._refresh_lists()

    def _refresh_lists(self) -> None:
        self._refresh_listbox(self.video_list, self.video_sources)
        self._refresh_listbox(self.audio_list, self.audio_sources)
        self._refresh_listbox(self.image_list, self.image_sources)
        self._refresh_listbox(self.url_list, self.url_sources)

    def _refresh_listbox(self, listbox: tk.Listbox, data: list[str]) -> None:
        listbox.delete(0, tk.END)
        for item in data:
            listbox.insert(tk.END, item)

    def _add_video_source(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Add video sources",
            filetypes=[("Video Files", "*.mp4 *.mov *.mkv *.avi *.webm")],
        )
        if paths:
            self.video_sources.extend(paths)
            self._refresh_lists()

    def _add_audio_source(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Add audio sources",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.flac *.m4a")],
        )
        if paths:
            self.audio_sources.extend(paths)
            self._refresh_lists()

    def _add_image_source(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Add image/GIF sources",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp")],
        )
        if paths:
            self.image_sources.extend(paths)
            self._refresh_lists()

    def _add_url_source(self, entry_widget: tk.Entry) -> None:
        url = entry_widget.get().strip()
        if url:
            self.url_sources.append(url)
            entry_widget.delete(0, tk.END)
            self._refresh_lists()

    def _remove_video_source(self) -> None:
        self._remove_selected(self.video_list, self.video_sources)

    def _remove_audio_source(self) -> None:
        self._remove_selected(self.audio_list, self.audio_sources)

    def _remove_image_source(self) -> None:
        self._remove_selected(self.image_list, self.image_sources)

    def _remove_url_source(self) -> None:
        self._remove_selected(self.url_list, self.url_sources)

    def _remove_selected(self, listbox: tk.Listbox, data: list[str]) -> None:
        selections = list(listbox.curselection())
        for index in reversed(selections):
            data.pop(index)
        self._refresh_lists()

    def _selected_effects(self) -> set[str]:
        return {name for name, var in self.effect_vars.items() if var.get()}

    def _run(self) -> None:
        config = ControllerConfig(
            input_path=self.input_path.get().strip(),
            output_path=self.output_path.get().strip(),
            segment_count=self.segment_count.get(),
            seed=self.seed_value.get().strip() or None,
            enabled_effects=self._selected_effects(),
            random_sound=self.random_sound.get(),
            overlay_enabled=self.overlay_enabled.get(),
            chaos_export=self.chaos_export.get(),
            sound_files=self.audio_sources,
            overlay_images=self.image_sources,
            overlay_videos=self.video_sources,
        )
        try:
            self._controller.generate(config)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Generation failed", str(exc))
        else:
            messagebox.showinfo("Done", "YTP remix generated!")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()

