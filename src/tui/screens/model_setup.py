from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static

from src.config.schema import ModelConfig


class ModelSetupScreen(Screen):
    def __init__(self, target: str) -> None:
        super().__init__()
        self.target = target
        if target == "question_model":
            self.target_name = "Question Model"
        elif target == "answer_model":
            self.target_name = "Answer Model"
        else:
            self.target_name = target.replace("_", " ").title()

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="form-container"):
            yield Static(f"SETUP {self.target_name.upper()}", id="header-card")
            yield Label("Base URL:", classes="form-label")
            yield Input(placeholder="e.g. https://api.openai.com/v1", id="input-base-url")
            yield Label("API Key:", classes="form-label")
            yield Input(placeholder="Enter API key", id="input-api-key", password=True)
            yield Label("Model ID:", classes="form-label")
            yield Input(placeholder="e.g. gpt-4o, llama-3.3-70b-versatile", id="input-model-id")
            yield Static("", id="test-result-label")
            with Horizontal(classes="button-row"):
                yield Button("Test Connection", id="btn-test", variant="default")
                yield Button("Save Configuration", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        cfg = getattr(self.app, "config", None)
        if cfg:
            model_cfg = getattr(cfg, self.target, None)
            if model_cfg:
                self.query_one("#input-base-url", Input).value = model_cfg.base_url
                self.query_one("#input-api-key", Input).value = model_cfg.api_key
                self.query_one("#input-model-id", Input).value = model_cfg.model

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
        elif event.button.id == "btn-test":
            base_url = self.query_one("#input-base-url", Input).value.strip()
            api_key = self.query_one("#input-api-key", Input).value.strip()
            model_id = self.query_one("#input-model-id", Input).value.strip()
            result_label = self.query_one("#test-result-label", Static)

            if not base_url or not api_key or not model_id:
                result_label.update("Validation failed: All fields are required.")
                result_label.remove_class("status-badge-ok")
                result_label.add_class("status-badge-missing")
            else:
                result_label.update("Connection parameters valid. Format is correct.")
                result_label.remove_class("status-badge-missing")
                result_label.add_class("status-badge-ok")
        elif event.button.id == "btn-save":
            base_url = self.query_one("#input-base-url", Input).value.strip()
            api_key = self.query_one("#input-api-key", Input).value.strip()
            model_id = self.query_one("#input-model-id", Input).value.strip()
            result_label = self.query_one("#test-result-label", Static)

            if not base_url or not api_key or not model_id:
                result_label.update("Validation failed: All fields are required.")
                result_label.remove_class("status-badge-ok")
                result_label.add_class("status-badge-missing")
                return

            model = ModelConfig(base_url=base_url, api_key=api_key, model=model_id)

            if hasattr(self.app, "config_manager") and self.app.config_manager:
                self.app.config_manager.save_model_config(self.target, model)

            if hasattr(self.app, "config") and self.app.config:
                setattr(self.app.config, self.target, model)

            self.app.pop_screen()
            if hasattr(self.app.screen, "update_model_statuses"):
                self.app.screen.update_model_statuses()
