import sys
from pathlib import Path
from unittest.mock import patch
import pytest

from src.config.config_manager import ConfigManager
from src.config.schema import AppConfig, ModelConfig


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


def test_app_initialization(tmp_path: Path):
    from src.tui.app import DatasetGeneratorApp

    cfg_file = tmp_path / "config.json"
    mgr = ConfigManager(config_path=cfg_file)
    q_model = ModelConfig(
        base_url="https://api.openai.com/v1",
        api_key="sk-test-12345678",
        model="gpt-4o",
    )
    mgr.save_model_config("question_model", q_model)

    app = DatasetGeneratorApp(config_manager=mgr)
    assert app.config_manager is mgr
    assert app.config is not None
    assert app.config.question_model is not None
    assert app.config.question_model.model == "gpt-4o"

    # Default init without passing config_manager
    default_app = DatasetGeneratorApp()
    assert isinstance(default_app.config_manager, ConfigManager)
    assert isinstance(default_app.config, AppConfig)
