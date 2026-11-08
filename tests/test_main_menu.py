from __future__ import annotations

from pathlib import Path
import pytest

from src.config.config_manager import ConfigManager
from src.config.schema import ModelConfig
from src.tui.app import DatasetGeneratorApp
from src.tui.screens.main_menu import MainMenuScreen


@pytest.mark.asyncio
async def test_main_menu_initial_status(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("src.config.config_manager.DEFAULT_CONFIG_PATH", tmp_path / "cfg.json")
    monkeypatch.setattr("src.config.config_manager.LOCAL_CONFIG_PATH", tmp_path / "local_cfg.json")
    app = DatasetGeneratorApp()
    async with app.run_test() as pilot:
        assert isinstance(app.screen, MainMenuScreen)
        status_q = app.screen.query_one("#status-question")
        assert "Not Configured" in str(status_q.render())
        status_a = app.screen.query_one("#status-answer")
        assert "Not Configured" in str(status_a.render())
        btn_start = app.screen.query_one("#btn-start")
        assert btn_start.disabled is True


@pytest.mark.asyncio
async def test_main_menu_with_models_configured(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    mgr = ConfigManager(config_path=cfg_file)
    mgr.save_model_config(
        "question_model",
        ModelConfig(
            base_url="https://api.openai.com/v1",
            api_key="sk-test-q-12345678",
            model="gpt-4o",
        ),
    )
    mgr.save_model_config(
        "answer_model",
        ModelConfig(
            base_url="https://api.openai.com/v1",
            api_key="sk-test-a-12345678",
            model="gpt-4o-mini",
        ),
    )
    app = DatasetGeneratorApp(config_manager=mgr)
    async with app.run_test() as pilot:
        assert isinstance(app.screen, MainMenuScreen)
        status_q = app.screen.query_one("#status-question")
        assert "Configured (gpt-4o)" in str(status_q.render())
        status_a = app.screen.query_one("#status-answer")
        assert "Configured (gpt-4o-mini)" in str(status_a.render())
        btn_start = app.screen.query_one("#btn-start")
        assert btn_start.disabled is False


@pytest.mark.asyncio
async def test_main_menu_exit_button(tmp_path: Path):
    app = DatasetGeneratorApp(config_manager=ConfigManager(config_path=tmp_path / "cfg.json"))
    async with app.run_test(size=(80, 40)) as pilot:
        assert isinstance(app.screen, MainMenuScreen)
        await pilot.click("#btn-exit")
        assert not app.is_running
