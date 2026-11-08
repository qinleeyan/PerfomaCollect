from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from src.config.schema import AppConfig, PreferencesConfig


class ViewConfigScreen(Screen):
    TITLE = "CURRENT CONFIGURATION"

    def __init__(self, config: AppConfig | None = None) -> None:
        super().__init__()
        self._config = config

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="form-container"):
            yield Static("CURRENT CONFIGURATION", id="header-card")
            yield Static("", id="config-details")
            with Horizontal(classes="button-row"):
                yield Button("Back", id="btn-back", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        self.update_config_display()

    def on_screen_resume(self) -> None:
        self.update_config_display()

    def update_config_display(self) -> None:
        cfg: AppConfig | None = self._config or getattr(self.app, "config", None)

        lines: list[str] = []

        lines.append("[b]Question Model:[/b]")
        if cfg and cfg.question_model:
            qm = cfg.question_model
            lines.append(f"  Base URL: {qm.base_url}")
            lines.append(f"  Model ID: {qm.model}")
            lines.append(f"  API Key:  {qm.masked_api_key}")
        else:
            lines.append("  Not Configured")
        lines.append("")

        lines.append("[b]Answer Model:[/b]")
        if cfg and cfg.answer_model:
            am = cfg.answer_model
            lines.append(f"  Base URL: {am.base_url}")
            lines.append(f"  Model ID: {am.model}")
            lines.append(f"  API Key:  {am.masked_api_key}")
        else:
            lines.append("  Not Configured")
        lines.append("")

        prefs = cfg.preferences if cfg and cfg.preferences else PreferencesConfig()
        lines.append("[b]Preferences:[/b]")
        lines.append(f"  Default Format:    {prefs.default_output_format}")
        lines.append(f"  Default Directory: {prefs.default_output_directory}")

        self.query_one("#config-details", Static).update("\n".join(lines))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
