"""Entry point for the Dual-Model Dataset Generator TUI application."""

from __future__ import annotations

from src.tui.app import DatasetGeneratorApp


def main() -> None:
    app = DatasetGeneratorApp()
    app.run()


if __name__ == "__main__":
    main()
