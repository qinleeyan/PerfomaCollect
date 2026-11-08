from __future__ import annotations

from pathlib import Path
import pytest
from textual.widgets import Static

from src.config.config_manager import ConfigManager
from src.config.schema import AppConfig, ModelConfig, PreferencesConfig
from src.tui.app import DatasetGeneratorApp
from src.tui.screens.main_menu import MainMenuScreen
from src.tui.screens.view_config import ViewConfigScreen


@pytest.mark.asyncio
async def test_view_config_display_with_configured_models(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    mgr = ConfigManager(config_path=cfg_file)
    q_key = "sk-question-secret-key-12345"
    a_key = "sk-answer-secret-key-67890"

    q_model = ModelConfig(
        base_url="https://api.openai.com/v1",
        api_key=q_key,
        model="gpt-4o",
    )
    a_model = ModelConfig(
        base_url="https://api.groq.com/openai/v1",
        api_key=a_key,
        model="llama-3.3-70b-versatile",
    )
    prefs = PreferencesConfig(
        default_output_format="jsonl",
        default_output_directory="./custom_output",
    )
    cfg = AppConfig(
        question_model=q_model,
        answer_model=a_model,
        preferences=prefs,
    )
    mgr.save_config(cfg)

    app = DatasetGeneratorApp(config_manager=mgr)
    async with app.run_test(size=(100, 40)) as pilot:
        await pilot.click("#btn-view-config")
        assert isinstance(app.screen, ViewConfigScreen)

        details_widget = app.screen.query_one("#config-details", Static)
        rendered_text = str(details_widget.render())
        full_screen_text = str(app.screen.render())

        # Verify Question Model base_url, model name, and masked API key
        assert "https://api.openai.com/v1" in rendered_text
        assert "gpt-4o" in rendered_text
        assert q_model.masked_api_key in rendered_text

        # Verify Answer Model base_url, model name, and masked API key
        assert "https://api.groq.com/openai/v1" in rendered_text
        assert "llama-3.3-70b-versatile" in rendered_text
        assert a_model.masked_api_key in rendered_text

        # Verify unmasked raw API key NEVER appears anywhere in the rendered output
        assert q_key not in rendered_text
        assert a_key not in rendered_text
        assert q_key not in full_screen_text
        assert a_key not in full_screen_text

        # Verify Preferences default_output_format and default_output_directory
        assert "jsonl" in rendered_text
        assert "./custom_output" in rendered_text


@pytest.mark.asyncio
async def test_view_config_display_unconfigured(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    mgr = ConfigManager(config_path=cfg_file)
    app = DatasetGeneratorApp(config_manager=mgr)
    async with app.run_test(size=(100, 40)) as pilot:
        await pilot.click("#btn-view-config")
        assert isinstance(app.screen, ViewConfigScreen)

        details_widget = app.screen.query_one("#config-details", Static)
        rendered_text = str(details_widget.render())

        assert "Not Configured" in rendered_text


@pytest.mark.asyncio
async def test_view_config_back_button(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    mgr = ConfigManager(config_path=cfg_file)
    app = DatasetGeneratorApp(config_manager=mgr)
    async with app.run_test(size=(100, 40)) as pilot:
        await pilot.click("#btn-view-config")
        assert isinstance(app.screen, ViewConfigScreen)

        await pilot.click("#btn-back")
        assert isinstance(app.screen, MainMenuScreen)
