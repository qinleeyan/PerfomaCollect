from __future__ import annotations

from pathlib import Path
import pytest
from textual.widgets import Input, Static

from src.config.config_manager import ConfigManager
from src.config.schema import ModelConfig
from src.tui.app import DatasetGeneratorApp
from src.tui.screens.main_menu import MainMenuScreen
from src.tui.screens.model_setup import ModelSetupScreen


@pytest.mark.asyncio
async def test_model_setup_prepopulation(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    mgr = ConfigManager(config_path=cfg_file)
    mgr.save_model_config(
        "question_model",
        ModelConfig(
            base_url="https://api.openai.com/v1",
            api_key="sk-test-prepop-key",
            model="gpt-4o",
        ),
    )
    app = DatasetGeneratorApp(config_manager=mgr)
    async with app.run_test(size=(80, 35)) as pilot:
        await pilot.click("#btn-setup-q")
        assert isinstance(app.screen, ModelSetupScreen)
        assert app.screen.query_one("#input-base-url", Input).value == "https://api.openai.com/v1"
        assert app.screen.query_one("#input-api-key", Input).value == "sk-test-prepop-key"
        assert app.screen.query_one("#input-model-id", Input).value == "gpt-4o"


@pytest.mark.asyncio
async def test_model_setup_save_flow(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    mgr = ConfigManager(config_path=cfg_file)
    app = DatasetGeneratorApp(config_manager=mgr)
    async with app.run_test(size=(80, 35)) as pilot:
        await pilot.click("#btn-setup-q")
        assert isinstance(app.screen, ModelSetupScreen)

        app.screen.query_one("#input-base-url", Input).value = "https://api.groq.com/openai/v1"
        app.screen.query_one("#input-api-key", Input).value = "gsk-test-key-12345"
        app.screen.query_one("#input-model-id", Input).value = "llama-3.3-70b-versatile"

        await pilot.click("#btn-save")

        assert isinstance(app.screen, MainMenuScreen)
        assert app.config.question_model is not None
        assert app.config.question_model.base_url == "https://api.groq.com/openai/v1"
        assert app.config.question_model.api_key == "gsk-test-key-12345"
        assert app.config.question_model.model == "llama-3.3-70b-versatile"

        # Check persisted to disk
        reloaded = mgr.load_config()
        assert reloaded.question_model is not None
        assert reloaded.question_model.model == "llama-3.3-70b-versatile"


@pytest.mark.asyncio
async def test_model_setup_validation(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    mgr = ConfigManager(config_path=cfg_file)
    app = DatasetGeneratorApp(config_manager=mgr)
    async with app.run_test(size=(80, 35)) as pilot:
        await pilot.click("#btn-setup-a")
        assert isinstance(app.screen, ModelSetupScreen)

        # Empty fields initially
        await pilot.click("#btn-save")

        # Screen should NOT have popped
        assert isinstance(app.screen, ModelSetupScreen)
        label = app.screen.query_one("#test-result-label", Static)
        assert "required" in str(label.render()).lower()
        assert app.config.answer_model is None


@pytest.mark.asyncio
async def test_model_setup_cancel(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    mgr = ConfigManager(config_path=cfg_file)
    app = DatasetGeneratorApp(config_manager=mgr)
    async with app.run_test(size=(80, 35)) as pilot:
        await pilot.click("#btn-setup-q")
        assert isinstance(app.screen, ModelSetupScreen)

        app.screen.query_one("#input-base-url", Input).value = "https://example.com"
        await pilot.click("#btn-cancel")

        assert isinstance(app.screen, MainMenuScreen)
        assert app.config.question_model is None


@pytest.mark.asyncio
async def test_model_setup_test_connection_click(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    mgr = ConfigManager(config_path=cfg_file)
    app = DatasetGeneratorApp(config_manager=mgr)
    async with app.run_test(size=(80, 35)) as pilot:
        await pilot.click("#btn-setup-q")
        assert isinstance(app.screen, ModelSetupScreen)

        # 1. Click test with empty fields -> error feedback
        await pilot.click("#btn-test")
        label = app.screen.query_one("#test-result-label", Static)
        assert "required" in str(label.render()).lower()

        # 2. Populate valid fields -> success feedback
        app.screen.query_one("#input-base-url", Input).value = "https://api.openai.com/v1"
        app.screen.query_one("#input-api-key", Input).value = "sk-test-valid-key"
        app.screen.query_one("#input-model-id", Input).value = "gpt-4o"

        await pilot.click("#btn-test")
        label = app.screen.query_one("#test-result-label", Static)
        text = str(label.render()).lower()
        assert "valid" in text or "passed" in text or "success" in text
        # Screen should remain on ModelSetupScreen
        assert isinstance(app.screen, ModelSetupScreen)
