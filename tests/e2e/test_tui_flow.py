from __future__ import annotations

from pathlib import Path
import pytest
from textual.widgets import Button, Input, RadioButton, Select, Static

from src.config.config_manager import ConfigManager
from src.tui.app import DatasetGeneratorApp
from src.tui.screens.generation_setup import GenerationSetupScreen
from src.tui.screens.main_menu import MainMenuScreen
from src.tui.screens.model_setup import ModelSetupScreen
from src.tui.screens.progress import ProgressScreen
from src.tui.screens.view_config import ViewConfigScreen


@pytest.mark.asyncio
async def test_full_tui_navigation_cycle(tmp_path: Path):
    """Test full TUI navigation cycle from initial unconfigured state to dataset generation progress.

    1. Main menu loads, verify btn-start is disabled initially.
    2. Click #btn-setup-q, fill Base URL, API Key, Model ID, click #btn-save.
    3. Click #btn-setup-a, fill Base URL, API Key, Model ID, click #btn-save.
    4. Return to Main menu, verify both models show 'Configured' and #btn-start is enabled.
    5. Click #btn-view-config, verify masked keys are shown, click #btn-back.
    6. Click #btn-start, fill topic 'Kucing', select mode and format, click #btn-start-job.
    7. Verify ProgressScreen is active with topic 'Kucing'.
    8. Click #btn-stop to safely return to previous screen.
    """
    config_path = tmp_path / "test_config.json"
    mgr = ConfigManager(config_path=config_path)
    app = DatasetGeneratorApp(config_manager=mgr)

    async with app.run_test(size=(100, 40)) as pilot:
        # 1. Main menu loads, verify btn-start is disabled initially
        assert isinstance(app.screen, MainMenuScreen)
        status_q = app.screen.query_one("#status-question", Static)
        status_a = app.screen.query_one("#status-answer", Static)
        assert "Not Configured" in str(status_q.render())
        assert "Not Configured" in str(status_a.render())

        btn_start = app.screen.query_one("#btn-start", Button)
        assert btn_start.disabled is True

        # 2. Click #btn-setup-q, fill Base URL, API Key, Model ID, click #btn-save
        await pilot.click("#btn-setup-q")
        await pilot.pause()
        assert isinstance(app.screen, ModelSetupScreen)

        app.screen.query_one("#input-base-url", Input).value = "https://api.openai.com/v1"
        app.screen.query_one("#input-api-key", Input).value = "sk-question-key-12345"
        app.screen.query_one("#input-model-id", Input).value = "gpt-4o"

        await pilot.click("#btn-save")
        await pilot.pause()

        # Check returned to MainMenu, question configured, but answer not yet configured
        assert isinstance(app.screen, MainMenuScreen)
        status_q = app.screen.query_one("#status-question", Static)
        assert "Configured (gpt-4o)" in str(status_q.render())
        btn_start = app.screen.query_one("#btn-start", Button)
        assert btn_start.disabled is True

        # 3. Click #btn-setup-a, fill Base URL, API Key, Model ID, click #btn-save
        await pilot.click("#btn-setup-a")
        await pilot.pause()
        assert isinstance(app.screen, ModelSetupScreen)

        app.screen.query_one("#input-base-url", Input).value = "https://api.groq.com/openai/v1"
        app.screen.query_one("#input-api-key", Input).value = "gsk-answer-key-67890"
        app.screen.query_one("#input-model-id", Input).value = "llama-3.3-70b-versatile"

        await pilot.click("#btn-save")
        await pilot.pause()

        # 4. Return to Main menu, verify both models show "Configured" and #btn-start is enabled
        assert isinstance(app.screen, MainMenuScreen)
        status_q = app.screen.query_one("#status-question", Static)
        status_a = app.screen.query_one("#status-answer", Static)
        assert "Configured (gpt-4o)" in str(status_q.render())
        assert "Configured (llama-3.3-70b-versatile)" in str(status_a.render())

        btn_start = app.screen.query_one("#btn-start", Button)
        assert btn_start.disabled is False

        # 5. Click #btn-view-config, verify masked keys are shown, click #btn-back
        await pilot.click("#btn-view-config")
        await pilot.pause()
        assert isinstance(app.screen, ViewConfigScreen)

        details_widget = app.screen.query_one("#config-details", Static)
        details_text = str(details_widget.render())
        assert "https://api.openai.com/v1" in details_text
        assert "gpt-4o" in details_text
        assert "https://api.groq.com/openai/v1" in details_text
        assert "llama-3.3-70b-versatile" in details_text

        # Verify masked API keys appear, raw keys never appear
        assert app.config.question_model is not None
        assert app.config.answer_model is not None
        assert app.config.question_model.masked_api_key in details_text
        assert app.config.answer_model.masked_api_key in details_text
        assert "sk-question-key-12345" not in details_text
        assert "gsk-answer-key-67890" not in details_text

        await pilot.click("#btn-back")
        await pilot.pause()
        assert isinstance(app.screen, MainMenuScreen)

        # 6. Click #btn-start, fill topic "Kucing", select mode and format, click #btn-start-job
        await pilot.click("#btn-start")
        await pilot.pause()
        assert isinstance(app.screen, GenerationSetupScreen)

        app.screen.query_one("#input-topic", Input).value = "Kucing"
        app.screen.query_one("#mode-limited", RadioButton).value = True
        app.screen.query_one("#input-target", Input).value = "25"
        app.screen.query_one("#select-format", Select).value = "jsonl"
        app.screen.query_one("#input-filename", Input).value = "dataset_kucing"

        await pilot.click("#btn-start-job")
        await pilot.pause()

        # 7. Verify ProgressScreen is active with topic "Kucing"
        assert isinstance(app.screen, ProgressScreen)
        assert app.screen.topic == "Kucing"
        assert app.screen.is_limited is True
        assert app.screen.target_count == 25
        assert app.screen.output_format == "jsonl"
        assert app.screen.filename == "dataset_kucing"

        info_lbl = app.screen.query_one("#lbl-job-info", Static)
        info_text = str(info_lbl.render())
        assert "Kucing" in info_text
        assert "Limited (25 records)" in info_text
        assert "JSONL" in info_text.upper()

        # 8. Click #btn-stop to safely return to previous screen
        await pilot.click("#btn-stop")
        await pilot.pause()

        assert not isinstance(app.screen, ProgressScreen)
        assert isinstance(app.screen, GenerationSetupScreen)

        await pilot.click("#btn-cancel")
        await pilot.pause()
        assert isinstance(app.screen, MainMenuScreen)


@pytest.mark.asyncio
async def test_full_tui_navigation_cycle_escape_stop(tmp_path: Path):
    """Test full TUI cycle stopping generation using escape key."""
    config_path = tmp_path / "test_config_escape.json"
    mgr = ConfigManager(config_path=config_path)
    app = DatasetGeneratorApp(config_manager=mgr)

    async with app.run_test(size=(100, 40)) as pilot:
        # Configure Question model
        await pilot.click("#btn-setup-q")
        await pilot.pause()
        app.screen.query_one("#input-base-url", Input).value = "https://api.openai.com/v1"
        app.screen.query_one("#input-api-key", Input).value = "sk-test-q"
        app.screen.query_one("#input-model-id", Input).value = "gpt-4o"
        await pilot.click("#btn-save")
        await pilot.pause()

        # Configure Answer model
        await pilot.click("#btn-setup-a")
        await pilot.pause()
        app.screen.query_one("#input-base-url", Input).value = "https://api.openai.com/v1"
        app.screen.query_one("#input-api-key", Input).value = "sk-test-a"
        app.screen.query_one("#input-model-id", Input).value = "gpt-4o-mini"
        await pilot.click("#btn-save")
        await pilot.pause()

        # Start job
        await pilot.click("#btn-start")
        await pilot.pause()
        app.screen.query_one("#input-topic", Input).value = "Kucing"
        await pilot.click("#btn-start-job")
        await pilot.pause()

        assert isinstance(app.screen, ProgressScreen)
        assert app.screen.topic == "Kucing"

        # Press escape to stop safely
        await pilot.press("escape")
        await pilot.pause()

        assert not isinstance(app.screen, ProgressScreen)
        assert isinstance(app.screen, GenerationSetupScreen)
