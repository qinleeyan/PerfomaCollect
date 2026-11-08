from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from src.config.schema import AppConfig, ModelConfig

LOCAL_CONFIG_PATH = Path("config.json")
GLOBAL_CONFIG_PATH = Path.home() / ".dual-model-generator" / "config.json"
DEFAULT_CONFIG_PATH = GLOBAL_CONFIG_PATH


class ConfigManager:
    def __init__(self, config_path: Path | None = None) -> None:
        self.explicit_path = config_path is not None
        if config_path:
            self.config_path = config_path
        elif LOCAL_CONFIG_PATH.exists():
            self.config_path = LOCAL_CONFIG_PATH
        elif DEFAULT_CONFIG_PATH.exists():
            self.config_path = DEFAULT_CONFIG_PATH
        else:
            self.config_path = LOCAL_CONFIG_PATH

    def load_config(self) -> AppConfig:
        if not self.config_path.exists():
            if not self.explicit_path and DEFAULT_CONFIG_PATH.exists():
                self.config_path = DEFAULT_CONFIG_PATH
            else:
                return AppConfig()
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return AppConfig.model_validate(data)
        except Exception:
            return AppConfig()

    def _write_atomic(self, target_path: Path, config: AppConfig) -> None:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        temp_fd, temp_path = tempfile.mkstemp(
            dir=target_path.parent, prefix="cfg_", suffix=".tmp"
        )
        try:
            with open(temp_fd, "w", encoding="utf-8") as f:
                json.dump(config.model_dump(), f, indent=2)
            os.replace(temp_path, target_path)
            try:
                os.chmod(target_path, 0o600)
            except OSError:
                pass
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

    def save_config(self, config: AppConfig) -> None:
        self._write_atomic(self.config_path, config)
        # If not a custom test path, also sync to both local and global
        if not self.explicit_path:
            if self.config_path != LOCAL_CONFIG_PATH:
                self._write_atomic(LOCAL_CONFIG_PATH, config)
            if self.config_path != GLOBAL_CONFIG_PATH:
                self._write_atomic(GLOBAL_CONFIG_PATH, config)

    def save_model_config(self, target: str, model_config: ModelConfig) -> AppConfig:
        cfg = self.load_config()
        if target == "question_model":
            cfg.question_model = model_config
        elif target == "answer_model":
            cfg.answer_model = model_config
        self.save_config(cfg)
        return cfg
