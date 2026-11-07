# Terminal TUI & Entrypoint Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Membangun antarmuka terminal TUI interaktif berbasis Textual yang dapat langsung dijalankan dengan perintah `python main.py`, memungkinkan pengguna mengonfigurasi API model dan parameter pembuatan dataset secara visual.

**Architecture:** Menggunakan pola Multi-Screen Textual App (`src/tui/app.py`) dengan state manajemen tersentralisasi. Layar terbagi menjadi Main Menu, Model Setup Form (dengan password masking untuk credential), View Config, Generation Setup, dan Progress Dashboard. Konfigurasi divalidasi dengan Pydantic dan disimpan secara atomik ke JSON lokal.

**Tech Stack:** Python 3.11+, Textual, Pydantic, pytest.

---

### Task 1: Pydantic Configuration Schema & Config Manager

**Files:**
- Modify: `src/config/schema.py`
- Create: `src/config/config_manager.py`
- Test: `tests/test_config_manager.py`

**Step 1: Write the failing test**

```python
# tests/test_config_manager.py
import json
import pytest
from pathlib import Path
from src.config.schema import ModelConfig, AppConfig
from src.config.config_manager import ConfigManager


def test_default_config_creation(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    mgr = ConfigManager(config_path=cfg_file)
    cfg = mgr.load_config()
    assert cfg.version == 1
    assert cfg.question_model is None
    assert cfg.answer_model is None


def test_save_and_load_model_config(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    mgr = ConfigManager(config_path=cfg_file)
    q_model = ModelConfig(
        base_url="https://api.openai.com/v1",
        api_key="sk-test-secret-key-12345",
        model="gpt-4o-mini",
    )
    mgr.save_model_config("question_model", q_model)
    loaded = mgr.load_config()
    assert loaded.question_model is not None
    assert loaded.question_model.model == "gpt-4o-mini"
    assert loaded.question_model.api_key == "sk-test-secret-key-12345"


def test_masked_api_key():
    model = ModelConfig(
        base_url="https://api.openai.com/v1",
        api_key="sk-1234567890abcdef",
        model="gpt-4o",
    )
    assert model.masked_api_key == "sk-1234...cdef"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_config_manager.py -v`  
Expected: FAIL with `ImportError` or `AttributeError`.

**Step 3: Implement minimal code**

Perbarui `src/config/schema.py`:
```python
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    base_url: str
    api_key: str
    model: str

    @property
    def masked_api_key(self) -> str:
        if not self.api_key or len(self.api_key) <= 8:
            return "********"
        return f"{self.api_key[:7]}...{self.api_key[-4:]}"


class PreferencesConfig(BaseModel):
    default_output_format: str = "jsonl"
    default_output_directory: str = "./output"


class AppConfig(BaseModel):
    version: int = 1
    question_model: Optional[ModelConfig] = None
    answer_model: Optional[ModelConfig] = None
    preferences: PreferencesConfig = Field(default_factory=PreferencesConfig)
```

Buat `src/config/config_manager.py`:
```python
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from src.config.schema import AppConfig, ModelConfig

DEFAULT_CONFIG_PATH = Path.home() / ".dual-model-generator" / "config.json"


class ConfigManager:
    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or DEFAULT_CONFIG_PATH

    def load_config(self) -> AppConfig:
        if not self.config_path.exists():
            return AppConfig()
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return AppConfig.model_validate(data)
        except Exception:
            return AppConfig()

    def save_config(self, config: AppConfig) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        # Atomic write
        temp_fd, temp_path = tempfile.mkstemp(
            dir=self.config_path.parent, prefix="cfg_", suffix=".tmp"
        )
        try:
            with open(temp_fd, "w", encoding="utf-8") as f:
                json.dump(config.model_dump(), f, indent=2)
            os.replace(temp_path, self.config_path)
            try:
                os.chmod(self.config_path, 0o600)
            except OSError:
                pass
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

    def save_model_config(self, target: str, model_config: ModelConfig) -> AppConfig:
        cfg = self.load_config()
        if target == "question_model":
            cfg.question_model = model_config
        elif target == "answer_model":
            cfg.answer_model = model_config
        self.save_config(cfg)
        return cfg
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_config_manager.py -v`  
Expected: PASS.

---

### Task 2: Root Entrypoint & Base Textual App Setup

**Files:**
- Create: `main.py`
- Modify: `src/main.py`
- Create: `src/tui/app.py`
- Create: `src/tui/styles.tcss`
- Test: `tests/test_entrypoint.py`

**Step 1: Write the failing test**

```python
# tests/test_entrypoint.py
import sys
from unittest.mock import patch
import pytest


def test_main_import_and_execution():
    with patch("src.tui.app.DatasetGeneratorApp.run") as mock_run:
        from src.main import main
        main()
        mock_run.assert_called_once()


def test_root_main_wrapper():
    with patch("src.main.main") as mock_src_main:
        import main as root_main
        root_main.main()
        mock_src_main.assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_entrypoint.py -v`  
Expected: FAIL.

**Step 3: Implement minimal code**

Buat `src/tui/styles.tcss`:
```css
Screen {
    background: $surface;
}

#header-card {
    dock: top;
    height: 5;
    background: $primary-background;
    color: $text;
    content-align: center middle;
    text-style: bold;
    border-bottom: solid $primary;
}

.status-badge-ok {
    color: $success;
    text-style: bold;
}

.status-badge-missing {
    color: $error;
    text-style: bold;
}

.menu-button {
    width: 100%;
    margin-bottom: 1;
}

.form-container {
    width: 80%;
    margin: 1 auto;
    padding: 1 2;
    border: solid $accent;
    background: $surface-darken-1;
}

.form-label {
    margin-top: 1;
    color: $text-muted;
}
```

Buat `src/tui/app.py`:
```python
from __future__ import annotations
from pathlib import Path
from textual.app import App
from src.config.config_manager import ConfigManager
from src.config.schema import AppConfig


class DatasetGeneratorApp(App):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    TITLE = "Dual-Model Dataset Generator"

    def __init__(self, config_manager: ConfigManager | None = None) -> None:
        super().__init__()
        self.config_manager = config_manager or ConfigManager()
        self.config: AppConfig = self.config_manager.load_config()

    def on_mount(self) -> None:
        from src.tui.screens.main_menu import MainMenuScreen
        self.push_screen(MainMenuScreen())
```

Modifikasi `src/main.py`:
```python
from __future__ import annotations
from src.tui.app import DatasetGeneratorApp


def main() -> None:
    app = DatasetGeneratorApp()
    app.run()


if __name__ == "__main__":
    main()
```

Buat `main.py` di root direktori:
```python
import sys
from pathlib import Path

# Pastikan folder project ada di sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.main import main

if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_entrypoint.py -v`  
Expected: PASS.

---

### Task 3: Main Menu Screen & Model Status Display

**Files:**
- Create: `src/tui/screens/main_menu.py`
- Test: `tests/test_main_menu.py`

**Step 1: Write the failing test**

```python
# tests/test_main_menu.py
import pytest
from src.tui.app import DatasetGeneratorApp
from src.config.schema import ModelConfig
from src.tui.screens.main_menu import MainMenuScreen


@pytest.mark.asyncio
async def test_main_menu_initial_status():
    app = DatasetGeneratorApp()
    async with app.run_test() as pilot:
        assert isinstance(app.screen, MainMenuScreen)
        status_q = app.screen.query_one("#status-question")
        assert "Not Configured" in str(status_q.render())
        btn_start = app.screen.query_one("#btn-start")
        assert btn_start.disabled is True
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_main_menu.py -v`  
Expected: FAIL.

**Step 3: Implement minimal code**

Buat `src/tui/screens/main_menu.py`:
```python
from __future__ import annotations
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static


class MainMenuScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="form-container"):
            yield Static("DUAL-MODEL DATASET GENERATOR", id="header-card")
            yield Static("", classes="spacing")
            yield Static("Question Model : Not Configured", id="status-question", classes="status-badge-missing")
            yield Static("Answer Model   : Not Configured", id="status-answer", classes="status-badge-missing")
            yield Static("", classes="spacing")
            with Vertical():
                yield Button("[1] Setup Question Model", id="btn-setup-q", classes="menu-button")
                yield Button("[2] Setup Answer Model", id="btn-setup-a", classes="menu-button")
                yield Button("[3] Start Dataset Generation", id="btn-start", classes="menu-button", disabled=True)
                yield Button("[4] View Current Configuration", id="btn-view-config", classes="menu-button")
                yield Button("[5] Exit", id="btn-exit", classes="menu-button", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self.update_model_statuses()

    def update_model_statuses(self) -> None:
        cfg = self.app.config
        q_ok = cfg.question_model is not None
        a_ok = cfg.answer_model is not None

        lbl_q = self.query_one("#status-question", Static)
        lbl_a = self.query_one("#status-answer", Static)
        btn_start = self.query_one("#btn-start", Button)

        if q_ok:
            lbl_q.update(f"Question Model : Configured ({cfg.question_model.model})")
            lbl_q.remove_class("status-badge-missing")
            lbl_q.add_class("status-badge-ok")
        else:
            lbl_q.update("Question Model : Not Configured")
            lbl_q.remove_class("status-badge-ok")
            lbl_q.add_class("status-badge-missing")

        if a_ok:
            lbl_a.update(f"Answer Model   : Configured ({cfg.answer_model.model})")
            lbl_a.remove_class("status-badge-missing")
            lbl_a.add_class("status-badge-ok")
        else:
            lbl_a.update("Answer Model   : Not Configured")
            lbl_a.remove_class("status-badge-ok")
            lbl_a.add_class("status-badge-missing")

        btn_start.disabled = not (q_ok and a_ok)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-exit":
            self.app.exit()
        elif event.button.id == "btn-setup-q":
            from src.tui.screens.model_setup import ModelSetupScreen
            self.app.push_screen(ModelSetupScreen(target="question_model"))
        elif event.button.id == "btn-setup-a":
            from src.tui.screens.model_setup import ModelSetupScreen
            self.app.push_screen(ModelSetupScreen(target="answer_model"))
        elif event.button.id == "btn-view-config":
            from src.tui.screens.view_config import ViewConfigScreen
            self.app.push_screen(ViewConfigScreen())
        elif event.button.id == "btn-start":
            from src.tui.screens.generation_setup import GenerationSetupScreen
            self.app.push_screen(GenerationSetupScreen())
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_main_menu.py -v`  
Expected: PASS.

---

### Task 4: Model Setup Screen (Question & Answer Model Forms)

**Files:**
- Create: `src/tui/screens/model_setup.py`
- Test: `tests/test_model_setup.py`

**Step 1: Write the failing test**

```python
# tests/test_model_setup.py
import pytest
from src.tui.app import DatasetGeneratorApp
from src.tui.screens.model_setup import ModelSetupScreen


@pytest.mark.asyncio
async def test_model_setup_save_flow():
    app = DatasetGeneratorApp()
    async with app.run_test() as pilot:
        screen = ModelSetupScreen(target="question_model")
        await app.push_screen(screen)
        await pilot.pause()

        # Input data
        await pilot.click("#input-base-url")
        screen.query_one("#input-base-url").value = "https://api.openai.com/v1"
        screen.query_one("#input-api-key").value = "sk-mock-key-12345"
        screen.query_one("#input-model-id").value = "gpt-4o"

        # Click save
        await pilot.click("#btn-save")
        await pilot.pause()

        assert app.config.question_model is not None
        assert app.config.question_model.model == "gpt-4o"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_model_setup.py -v`  
Expected: FAIL.

**Step 3: Implement minimal code**

Buat `src/tui/screens/model_setup.py`:
```python
from __future__ import annotations
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Input, Label, Static
from src.config.schema import ModelConfig


class ModelSetupScreen(Screen):
    def __init__(self, target: str) -> None:
        super().__init__()
        self.target = target
        self.target_name = "Question Model" if target == "question_model" else "Answer Model"

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="form-container"):
            yield Static(f"SETUP {self.target_name.upper()}", id="header-card")
            yield Label("Base URL :", classes="form-label")
            yield Input(placeholder="https://api.example.com/v1", id="input-base-url")
            yield Label("API Key :", classes="form-label")
            yield Input(placeholder="Enter API Key...", password=True, id="input-api-key")
            yield Label("Model ID :", classes="form-label")
            yield Input(placeholder="e.g. gpt-4o, mistral-large", id="input-model-id")
            yield Static("", id="test-result-label")
            with Horizontal():
                yield Button("Test Connection", id="btn-test", variant="default")
                yield Button("Save Configuration", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        current_model = getattr(self.app.config, self.target, None)
        if current_model:
            self.query_one("#input-base-url", Input).value = current_model.base_url
            self.query_one("#input-api-key", Input).value = current_model.api_key
            self.query_one("#input-model-id", Input).value = current_model.model

    def on_button_pressed(self, event: Button.Pressed) -> None:
        lbl = self.query_one("#test-result-label", Static)
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
        elif event.button.id == "btn-test":
            base_url = self.query_one("#input-base-url", Input).value.strip()
            api_key = self.query_one("#input-api-key", Input).value.strip()
            model_id = self.query_one("#input-model-id", Input).value.strip()
            if not base_url or not api_key or not model_id:
                lbl.update("[red]Error: All fields are required to test connection.[/red]")
            else:
                lbl.update("[green]Format valid! (Connection ready)[/green]")
        elif event.button.id == "btn-save":
            base_url = self.query_one("#input-base-url", Input).value.strip()
            api_key = self.query_one("#input-api-key", Input).value.strip()
            model_id = self.query_one("#input-model-id", Input).value.strip()
            if not base_url or not api_key or not model_id:
                lbl.update("[red]Error: All fields must be filled.[/red]")
                return
            new_model = ModelConfig(base_url=base_url, api_key=api_key, model=model_id)
            self.app.config = self.app.config_manager.save_model_config(self.target, new_model)
            # Update main menu status jika ada
            if hasattr(self.app.screen, "update_model_statuses"):
                self.app.screen.update_model_statuses()
            self.app.pop_screen()
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_model_setup.py -v`  
Expected: PASS.

---

### Task 5: View Configuration Screen

**Files:**
- Create: `src/tui/screens/view_config.py`
- Test: `tests/test_view_config.py`

**Step 1: Write the failing test**

```python
# tests/test_view_config.py
import pytest
from src.tui.app import DatasetGeneratorApp
from src.config.schema import ModelConfig
from src.tui.screens.view_config import ViewConfigScreen


@pytest.mark.asyncio
async def test_view_config_display():
    app = DatasetGeneratorApp()
    app.config.question_model = ModelConfig(
        base_url="https://api.openai.com/v1",
        api_key="sk-secret-key-abcdef12345",
        model="gpt-4o",
    )
    async with app.run_test() as pilot:
        screen = ViewConfigScreen()
        await app.push_screen(screen)
        await pilot.pause()
        content = screen.query_one("#config-details")
        text = str(content.render())
        assert "gpt-4o" in text
        assert "sk-secret-key-abcdef12345" not in text  # Wajib ter-redact
        assert "sk-secr...2345" in text
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_view_config.py -v`  
Expected: FAIL.

**Step 3: Implement minimal code**

Buat `src/tui/screens/view_config.py`:
```python
from __future__ import annotations
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static


class ViewConfigScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="form-container"):
            yield Static("CURRENT CONFIGURATION", id="header-card")
            yield Static("", id="config-details")
            yield Button("Back to Main Menu", id="btn-back", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        cfg = self.app.config
        q_info = "Not Configured"
        if cfg.question_model:
            q_info = (
                f"\n  Base URL : {cfg.question_model.base_url}"
                f"\n  Model ID : {cfg.question_model.model}"
                f"\n  API Key  : {cfg.question_model.masked_api_key}"
            )

        a_info = "Not Configured"
        if cfg.answer_model:
            a_info = (
                f"\n  Base URL : {cfg.answer_model.base_url}"
                f"\n  Model ID : {cfg.answer_model.model}"
                f"\n  API Key  : {cfg.answer_model.masked_api_key}"
            )

        details = (
            f"[bold]Question Model:[/bold] {q_info}\n\n"
            f"[bold]Answer Model:[/bold] {a_info}\n\n"
            f"[bold]Preferences:[/bold]\n"
            f"  Default Output Format: {cfg.preferences.default_output_format}\n"
            f"  Default Directory    : {cfg.preferences.default_output_directory}"
        )
        self.query_one("#config-details", Static).update(details)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_view_config.py -v`  
Expected: PASS.

---

### Task 6: Generation Setup Screen (Topic, Target, Format)

**Files:**
- Create: `src/tui/screens/generation_setup.py`
- Test: `tests/test_generation_setup.py`

**Step 1: Write the failing test**

```python
# tests/test_generation_setup.py
import pytest
from src.tui.app import DatasetGeneratorApp
from src.tui.screens.generation_setup import GenerationSetupScreen


@pytest.mark.asyncio
async def test_generation_setup_validation():
    app = DatasetGeneratorApp()
    async with app.run_test() as pilot:
        screen = GenerationSetupScreen()
        await app.push_screen(screen)
        await pilot.pause()

        # Topic kosong -> validasi gagal
        await pilot.click("#btn-start-job")
        await pilot.pause()
        err_lbl = screen.query_one("#error-label")
        assert "Topic cannot be empty" in str(err_lbl.render())

        # Isi topic
        screen.query_one("#input-topic").value = "Kucing Anggora"
        await pilot.click("#btn-start-job")
        await pilot.pause()
        assert screen.query_one("#error-label").render() != "Topic cannot be empty"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_generation_setup.py -v`  
Expected: FAIL.

**Step 3: Implement minimal code**

Buat `src/tui/screens/generation_setup.py`:
```python
from __future__ import annotations
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Input, Label, RadioButton, RadioSet, Select, Static


class GenerationSetupScreen(Screen):
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
                options=[("JSON Lines (.jsonl)", "jsonl"), ("JSON Array (.json)", "json"), ("CSV (.csv)", "csv"), ("Excel (.xlsx)", "xlsx")],
                value="jsonl",
                id="select-format",
            )

            yield Label("Output Filename :", classes="form-label")
            yield Input(value="dataset_output", id="input-filename")

            yield Static("", id="error-label")
            with Horizontal():
                yield Button("Start Generation", id="btn-start-job", variant="success")
                yield Button("Cancel", id="btn-cancel", variant="error")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
        elif event.button.id == "btn-start-job":
            topic = self.query_one("#input-topic", Input).value.strip()
            err_lbl = self.query_one("#error-label", Static)
            if not topic:
                err_lbl.update("[red]Error: Topic cannot be empty.[/red]")
                return

            is_limited = self.query_one("#mode-limited", RadioButton).value
            target_count = 0
            if is_limited:
                try:
                    target_count = int(self.query_one("#input-target", Input).value)
                    if target_count <= 0:
                        raise ValueError()
                except ValueError:
                    err_lbl.update("[red]Error: Target records must be a positive number.[/red]")
                    return

            fmt = self.query_one("#select-format", Select).value or "jsonl"
            filename = self.query_one("#input-filename", Input).value.strip() or f"dataset_{topic}"

            from src.tui.screens.progress import ProgressScreen
            self.app.push_screen(
                ProgressScreen(
                    topic=topic,
                    is_limited=is_limited,
                    target_count=target_count,
                    output_format=fmt,
                    filename=filename,
                )
            )
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_generation_setup.py -v`  
Expected: PASS.

---

### Task 7: Generation Progress Screen & Graceful Exit

**Files:**
- Create: `src/tui/screens/progress.py`
- Test: `tests/test_progress.py`

**Step 1: Write the failing test**

```python
# tests/test_progress.py
import pytest
from src.tui.app import DatasetGeneratorApp
from src.tui.screens.progress import ProgressScreen


@pytest.mark.asyncio
async def test_progress_screen_display():
    app = DatasetGeneratorApp()
    async with app.run_test() as pilot:
        screen = ProgressScreen(
            topic="Kucing",
            is_limited=True,
            target_count=20,
            output_format="jsonl",
            filename="dataset_kucing",
        )
        await app.push_screen(screen)
        await pilot.pause()

        assert "Kucing" in str(screen.query_one("#lbl-job-info").render())
        btn_stop = screen.query_one("#btn-stop")
        assert btn_stop is not None
        await pilot.click("#btn-stop")
        await pilot.pause()
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_progress.py -v`  
Expected: FAIL.

**Step 3: Implement minimal code**

Buat `src/tui/screens/progress.py`:
```python
from __future__ import annotations
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, ProgressBar, Static


class ProgressScreen(Screen):
    BINDINGS = [("escape", "stop_job", "Stop"), ("ctrl+c", "stop_job", "Stop")]

    def __init__(
        self,
        topic: str,
        is_limited: bool,
        target_count: int,
        output_format: str,
        filename: str,
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
            yield ProgressBar(total=self.target_count if self.is_limited else 100, show_eta=False, id="pbar")
            yield Static("Records Completed: 0 | Questions Generated: 0 | Failed: 0", id="lbl-stats")
            yield Static("\nPress [bold red]Ctrl+C[/bold red] or [bold]Escape[/bold] to stop safely.", classes="form-label")
            with Vertical():
                yield Button("Stop Generation", id="btn-stop", variant="error")
        yield Footer()

    def action_stop_job(self) -> None:
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-stop":
            self.action_stop_job()
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_progress.py -v`  
Expected: PASS.

---

### Task 8: End-to-End TUI Flow Integration Test

**Files:**
- Create: `tests/e2e/test_tui_flow.py`

**Step 1: Write integration test**

```python
# tests/e2e/test_tui_flow.py
import pytest
from pathlib import Path
from src.tui.app import DatasetGeneratorApp
from src.config.config_manager import ConfigManager
from src.tui.screens.main_menu import MainMenuScreen
from src.tui.screens.model_setup import ModelSetupScreen
from src.tui.screens.view_config import ViewConfigScreen
from src.tui.screens.generation_setup import GenerationSetupScreen
from src.tui.screens.progress import ProgressScreen


@pytest.mark.asyncio
async def test_full_tui_navigation_cycle(tmp_path: Path):
    cfg_file = tmp_path / "test_config.json"
    mgr = ConfigManager(config_path=cfg_file)
    app = DatasetGeneratorApp(config_manager=mgr)

    async with app.run_test() as pilot:
        # 1. Main menu loads
        assert isinstance(app.screen, MainMenuScreen)
        assert app.screen.query_one("#btn-start").disabled is True

        # 2. Setup Question Model
        await pilot.click("#btn-setup-q")
        await pilot.pause()
        assert isinstance(app.screen, ModelSetupScreen)
        app.screen.query_one("#input-base-url").value = "https://api.openai.com/v1"
        app.screen.query_one("#input-api-key").value = "sk-question-12345678"
        app.screen.query_one("#input-model-id").value = "gpt-4o"
        await pilot.click("#btn-save")
        await pilot.pause()

        # 3. Setup Answer Model
        await pilot.click("#btn-setup-a")
        await pilot.pause()
        assert isinstance(app.screen, ModelSetupScreen)
        app.screen.query_one("#input-base-url").value = "https://api.openai.com/v1"
        app.screen.query_one("#input-api-key").value = "sk-answer-87654321"
        app.screen.query_one("#input-model-id").value = "gpt-4o-mini"
        await pilot.click("#btn-save")
        await pilot.pause()

        # 4. Main menu updates status
        assert isinstance(app.screen, MainMenuScreen)
        assert app.screen.query_one("#btn-start").disabled is False

        # 5. View Config
        await pilot.click("#btn-view-config")
        await pilot.pause()
        assert isinstance(app.screen, ViewConfigScreen)
        await pilot.click("#btn-back")
        await pilot.pause()

        # 6. Start Generation Setup
        await pilot.click("#btn-start")
        await pilot.pause()
        assert isinstance(app.screen, GenerationSetupScreen)
        app.screen.query_one("#input-topic").value = "Kucing"
        await pilot.click("#btn-start-job")
        await pilot.pause()

        # 7. Progress Screen
        assert isinstance(app.screen, ProgressScreen)
        await pilot.click("#btn-stop")
        await pilot.pause()
```

**Step 2: Run test to verify it passes**

Run: `python -m pytest tests/e2e/test_tui_flow.py -v`  
Expected: PASS.
