from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, ProgressBar, Static


class ProgressScreen(Screen):
    BINDINGS = [("escape", "stop_job", "Stop"), ("ctrl+c", "stop_job", "Stop")]

    def __init__(
        self,
        topic: str,
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

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="form-container"):
            yield Static("GENERATION IN PROGRESS", id="header-card")
            mode_str = f"Limited ({self.target_count} records)" if self.is_limited else "Unlimited Mode"
            info = (
                f"Topic: [bold]{self.topic}[/bold] | Mode: {mode_str} | "
                f"Format: {self.output_format.upper()} | File: {self.filename}.{self.output_format}"
            )
            yield Static(info, id="lbl-job-info")
            yield Static("Current Stage: [yellow]Ready / Standing By[/yellow]", id="lbl-stage")
            yield ProgressBar(
                total=self.target_count if self.is_limited else 100,
                show_eta=False,
                id="pbar",
            )
            yield Static("Records Completed: 0 | Questions Generated: 0 | Failed: 0", id="lbl-stats")
            yield Static("Press [bold red]Ctrl+C[/bold red] or [bold]Escape[/bold] to stop safely.", classes="form-label")
            with Vertical():
                yield Button("Stop Generation", id="btn-stop", variant="error")
        yield Footer()

    def action_stop_job(self) -> None:
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-stop":
            self.action_stop_job()
