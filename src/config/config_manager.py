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
