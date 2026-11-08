from __future__ import annotations

from pathlib import Path
import pytest
from textual.widgets import Input, RadioButton, RadioSet, Select, Static

from src.config.config_manager import ConfigManager
from src.config.schema import ModelConfig
from src.tui.app import DatasetGeneratorApp
from src.tui.screens.generation_setup import GenerationSetupScreen
from src.tui.screens.main_menu import MainMenuScreen


@pytest.mark.asyncio
async def test_generation_setup_empty_topic_validation():
    app = DatasetGeneratorApp()
    async with app.run_test(size=(80, 35)) as pilot:
        screen = GenerationSetupScreen()
        await app.push_screen(screen)
        await pilot.pause()

        assert isinstance(app.screen, GenerationSetupScreen)
        # Attempt to start without entering topic
        await pilot.click("#btn-start-job")
        await pilot.pause()

        # Validation should fail, screen must not pop or transition
        assert isinstance(app.screen, GenerationSetupScreen)
        err_lbl = screen.query_one("#error-label", Static)
        err_text = str(err_lbl.render()).lower()
        assert "topic" in err_text
        assert "empty" in err_text or "required" in err_text


@pytest.mark.asyncio
async def test_generation_setup_target_count_validation():
    app = DatasetGeneratorApp()
    async with app.run_test(size=(80, 35)) as pilot:
        screen = GenerationSetupScreen()
        await app.push_screen(screen)
        await pilot.pause()

        # Provide a valid topic
        screen.query_one("#input-topic", Input).value = "Machine Learning"

        # 1. Target count <= 0
        screen.query_one("#input-target", Input).value = "0"
        await pilot.click("#btn-start-job")
        await pilot.pause()

        assert isinstance(app.screen, GenerationSetupScreen)
        err_lbl = screen.query_one("#error-label", Static)
        err_text = str(err_lbl.render()).lower()
        assert "target" in err_text or "positive" in err_text or "invalid" in err_text

        # 2. Negative target count
        screen.query_one("#input-target", Input).value = "-5"
        await pilot.click("#btn-start-job")
        await pilot.pause()

        assert isinstance(app.screen, GenerationSetupScreen)
        err_lbl = screen.query_one("#error-label", Static)
        err_text = str(err_lbl.render()).lower()
        assert "target" in err_text or "positive" in err_text or "invalid" in err_text

        # 3. Non-integer target count
        screen.query_one("#input-target", Input).value = "abc"
        await pilot.click("#btn-start-job")
        await pilot.pause()

        assert isinstance(app.screen, GenerationSetupScreen)
        err_lbl = screen.query_one("#error-label", Static)
        err_text = str(err_lbl.render()).lower()
        assert "target" in err_text or "number" in err_text or "integer" in err_text or "invalid" in err_text


@pytest.mark.asyncio
async def test_generation_setup_cancel_button():
    app = DatasetGeneratorApp()
    async with app.run_test(size=(80, 35)) as pilot:
        screen = GenerationSetupScreen()
        await app.push_screen(screen)
        await pilot.pause()

        assert isinstance(app.screen, GenerationSetupScreen)
        await pilot.click("#btn-cancel")
        await pilot.pause()

        # Screen should pop back to MainMenuScreen
        assert isinstance(app.screen, MainMenuScreen)


@pytest.mark.asyncio
async def test_generation_setup_submit_valid():
    app = DatasetGeneratorApp()
    async with app.run_test(size=(80, 35)) as pilot:
        screen = GenerationSetupScreen()
        await app.push_screen(screen)
        await pilot.pause()

        # Fill valid form fields in limited mode
        screen.query_one("#input-topic", Input).value = "Quantum Computing"
        screen.query_one("#input-target", Input).value = "25"
        screen.query_one("#select-format", Select).value = "csv"
        screen.query_one("#input-filename", Input).value = "quantum_dataset"

        await pilot.click("#btn-start-job")
        await pilot.pause()

        # Screen should transition away from GenerationSetupScreen
        assert not isinstance(app.screen, GenerationSetupScreen)
        assert app.screen.__class__.__name__ == "ProgressScreen"
        assert getattr(app.screen, "topic") == "Quantum Computing"
        assert getattr(app.screen, "is_limited") is True
        assert getattr(app.screen, "target_count") == 25
        assert getattr(app.screen, "output_format") == "csv"
        assert getattr(app.screen, "filename") == "quantum_dataset"


@pytest.mark.asyncio
async def test_generation_setup_unlimited_mode():
    app = DatasetGeneratorApp()
    async with app.run_test(size=(80, 35)) as pilot:
        screen = GenerationSetupScreen()
        await app.push_screen(screen)
        await pilot.pause()

        # Switch to unlimited mode
        screen.query_one("#mode-unlimited", RadioButton).value = True
        await pilot.pause()

        # Verify target input is disabled
        assert screen.query_one("#input-target", Input).disabled is True

        screen.query_one("#input-topic", Input).value = "Space Exploration"
        screen.query_one("#select-format", Select).value = "json"

        # Even with empty/invalid target count, unlimited mode proceeds
        screen.query_one("#input-target", Input).value = ""
        await pilot.click("#btn-start-job")
        await pilot.pause()

        assert not isinstance(app.screen, GenerationSetupScreen)
        assert app.screen.__class__.__name__ == "ProgressScreen"
        assert getattr(app.screen, "topic") == "Space Exploration"
        assert getattr(app.screen, "is_limited") is False
        assert getattr(app.screen, "target_count") == 0
        assert getattr(app.screen, "output_format") == "json"


@pytest.mark.asyncio
async def test_generation_setup_navigation_from_main_menu(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    mgr = ConfigManager(config_path=cfg_file)
    mgr.save_model_config(
        "question_model",
        ModelConfig(base_url="https://api.openai.com/v1", api_key="sk-q", model="gpt-4o"),
    )
    mgr.save_model_config(
        "answer_model",
        ModelConfig(base_url="https://api.openai.com/v1", api_key="sk-a", model="gpt-4o-mini"),
    )

    app = DatasetGeneratorApp(config_manager=mgr)
    async with app.run_test(size=(80, 35)) as pilot:
        assert isinstance(app.screen, MainMenuScreen)
        btn_start = app.screen.query_one("#btn-start")
        assert not btn_start.disabled

        await pilot.click("#btn-start")
        await pilot.pause()

        assert isinstance(app.screen, GenerationSetupScreen)
