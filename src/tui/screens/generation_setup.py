from __future__ import annotations

import re
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    RadioButton,
    RadioSet,
    Select,
    Static,
)

try:
    from src.tui.screens.progress import ProgressScreen
except (ImportError, ModuleNotFoundError):
    class ProgressScreen(Screen):  # type: ignore[no-redef]
        def __init__(
            self,
            topic: str = "",
            is_limited: bool = True,
            target_count: int = 50,
            output_format: str = "jsonl",
            filename: str = "dataset_output",
        ) -> None:
            super().__init__()
            self.topic = topic
            self.is_limited = is_limited
            self.target_count = target_count
            self.output_format = output_format
            self.filename = filename


class GenerationSetupScreen(Screen):
    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+c", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="form-container"):
            yield Static("NEW DATASET GENERATION", id="header-card")

            yield Label("Topic :", classes="form-label")
            yield Input(placeholder="e.g. Kucing, Deep Learning, Resep Masakan", id="input-topic")

            yield Label("Generation Mode :", classes="form-label")
            with RadioSet(id="radio-mode"):
                yield RadioButton("Limited (Specify target records)", value=True, id="mode-limited")
                yield RadioButton("Unlimited (Continue until stopped)", id="mode-unlimited")

            yield Label("Target Records (Limited Mode) :", classes="form-label", id="lbl-target")
            yield Input(value="50", id="input-target", type="integer")

            yield Label("Output Format :", classes="form-label")
            yield Select[str](
                options=[
                    ("JSON Lines (.jsonl)", "jsonl"),
                    ("JSON Array (.json)", "json"),
                    ("CSV (.csv)", "csv"),
                    ("Excel (.xlsx)", "xlsx"),
                ],
                value="jsonl",
                id="select-format",
                allow_blank=False,
            )

            yield Label("Output Filename :", classes="form-label")
            yield Input(value="dataset_output", id="input-filename")

            yield Static("", id="error-label")
            with Horizontal(classes="button-row"):
                yield Button("Start Generation", id="btn-start-job", variant="success")
                yield Button("Cancel", id="btn-cancel", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        cfg = getattr(self.app, "config", None)
        if cfg and hasattr(cfg, "preferences") and cfg.preferences:
            pref_fmt = getattr(cfg.preferences, "default_output_format", None)
            if pref_fmt:
                select = self.query_one("#select-format", Select)
                select.value = pref_fmt

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        if event.radio_set.id == "radio-mode":
            is_limited = self.query_one("#mode-limited", RadioButton).value
            target_input = self.query_one("#input-target", Input)
            target_input.disabled = not is_limited

    def action_cancel(self) -> None:
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-start-job":
            topic = self.query_one("#input-topic", Input).value.strip()
            err_lbl = self.query_one("#error-label", Static)

            if not topic:
                err_lbl.update("Error: Topic cannot be empty. Topic is required.")
                return

            is_limited = self.query_one("#mode-limited", RadioButton).value
            target_count = 0
            if is_limited:
                raw_target = self.query_one("#input-target", Input).value.strip()
                try:
                    target_count = int(raw_target)
                    if target_count <= 0:
                        raise ValueError("Must be positive")
                except (ValueError, TypeError):
                    err_lbl.update("Error: Target records must be a positive integer.")
                    return

            format_select = self.query_one("#select-format", Select)
            if not format_select.is_blank() and format_select.value:
                fmt = str(format_select.value)
            else:
                fmt = "jsonl"

            filename = self.query_one("#input-filename", Input).value.strip() or f"dataset_{topic}"

            try:
                from src.tui.screens.progress import ProgressScreen as TargetProgressScreen
            except (ImportError, ModuleNotFoundError):
                TargetProgressScreen = ProgressScreen

            self.app.push_screen(
                TargetProgressScreen(
                    topic=topic,
                    is_limited=is_limited,
                    target_count=target_count,
                    output_format=fmt,
                    filename=filename,
                )
            )
