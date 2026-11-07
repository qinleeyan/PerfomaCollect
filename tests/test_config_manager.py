from pathlib import Path
import pytest
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
    assert (cfg_file.stat().st_mode & 0o777) == 0o600


def test_masked_api_key():
    model = ModelConfig(
        base_url="https://api.openai.com/v1",
        api_key="sk-1234567890abcdef",
        model="gpt-4o",
    )
    assert model.masked_api_key == "sk-1234...cdef"

    short_model = ModelConfig(
        base_url="https://api.openai.com/v1",
        api_key="sk-short",
        model="gpt-4o",
    )
    assert short_model.masked_api_key == "********"
