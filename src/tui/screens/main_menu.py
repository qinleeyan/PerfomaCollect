from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static


class MainMenuScreen(Screen):
    BINDINGS = [
        ("1", "setup_q", "1: Question Model"),
        ("2", "setup_a", "2: Answer Model"),
        ("3", "start_gen", "3: Start"),
        ("4", "view_cfg", "4: View Config"),
        ("5", "exit_app", "5: Exit"),
        ("q", "exit_app", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="form-container"):
            yield Static("DUAL-MODEL DATASET GENERATOR", id="header-card")
            yield Static("Question Model : Not Configured", id="status-question", classes="status-badge-missing")
            yield Static("Answer Model   : Not Configured", id="status-answer", classes="status-badge-missing")
            with Vertical(id="menu-buttons-container"):
                yield Button("[1] Setup Question Model", id="btn-setup-q", classes="menu-button")
                yield Button("[2] Setup Answer Model", id="btn-setup-a", classes="menu-button")
                yield Button("[3] Start Dataset Generation", id="btn-start", classes="menu-button", disabled=True)
                yield Button("[4] View Current Configuration", id="btn-view-config", classes="menu-button")
                yield Button("[5] Exit", id="btn-exit", classes="menu-button", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self.update_model_statuses()

    def on_screen_resume(self) -> None:
        self.update_model_statuses()

    def update_model_statuses(self) -> None:
        cfg = getattr(self.app, "config", None)
        q_ok = bool(cfg and cfg.question_model is not None)
        a_ok = bool(cfg and cfg.answer_model is not None)

        lbl_q = self.query_one("#status-question", Static)
        lbl_a = self.query_one("#status-answer", Static)
        btn_start = self.query_one("#btn-start", Button)

        if q_ok and cfg.question_model:
            lbl_q.update(f"Question Model : Configured ({cfg.question_model.model})")
            lbl_q.remove_class("status-badge-missing")
            lbl_q.add_class("status-badge-ok")
        else:
            lbl_q.update("Question Model : Not Configured")
            lbl_q.remove_class("status-badge-ok")
            lbl_q.add_class("status-badge-missing")

        if a_ok and cfg.answer_model:
            lbl_a.update(f"Answer Model   : Configured ({cfg.answer_model.model})")
            lbl_a.remove_class("status-badge-missing")
            lbl_a.add_class("status-badge-ok")
        else:
            lbl_a.update("Answer Model   : Not Configured")
            lbl_a.remove_class("status-badge-ok")
            lbl_a.add_class("status-badge-missing")

        btn_start.disabled = not (q_ok and a_ok)

    def action_setup_q(self) -> None:
        from src.tui.screens.model_setup import ModelSetupScreen
        self.app.push_screen(ModelSetupScreen(target="question_model"))

    def action_setup_a(self) -> None:
        from src.tui.screens.model_setup import ModelSetupScreen
        self.app.push_screen(ModelSetupScreen(target="answer_model"))

    def action_start_gen(self) -> None:
        cfg = getattr(self.app, "config", None)
        q_ok = bool(cfg and cfg.question_model is not None)
        a_ok = bool(cfg and cfg.answer_model is not None)
        if not (q_ok and a_ok):
            self.notify("Both Question and Answer models must be configured first!", severity="warning")
            return
        from src.tui.screens.generation_setup import GenerationSetupScreen
        self.app.push_screen(GenerationSetupScreen())

    def action_view_cfg(self) -> None:
        from src.tui.screens.view_config import ViewConfigScreen
        self.app.push_screen(ViewConfigScreen())

    def action_exit_app(self) -> None:
        self.app.exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-exit":
            self.action_exit_app()
        elif event.button.id == "btn-setup-q":
            self.action_setup_q()
        elif event.button.id == "btn-setup-a":
            self.action_setup_a()
        elif event.button.id == "btn-view-config":
            self.action_view_cfg()
        elif event.button.id == "btn-start":
            self.action_start_gen()
