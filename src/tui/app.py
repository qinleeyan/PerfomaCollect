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
        try:
            from src.tui.screens.main_menu import MainMenuScreen
            self.push_screen(MainMenuScreen())
        except (ImportError, ModuleNotFoundError):
            pass
