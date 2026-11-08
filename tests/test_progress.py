from __future__ import annotations

import pytest
from textual.widgets import ProgressBar, Static

from src.tui.app import DatasetGeneratorApp
from src.tui.screens.progress import ProgressScreen


@pytest.mark.asyncio
async def test_progress_screen_display_limited():
    app = DatasetGeneratorApp()
    async with app.run_test(size=(80, 35)) as pilot:
        screen = ProgressScreen(
            topic="Kucing",
            is_limited=True,
            target_count=50,
            output_format="jsonl",
            filename="dataset_kucing",
        )
        await app.push_screen(screen)
        await pilot.pause()

        assert isinstance(app.screen, ProgressScreen)

        # Header card "GENERATION IN PROGRESS" is rendered
        hdr = screen.query_one("#header-card", Static)
        assert "GENERATION IN PROGRESS" in str(hdr.render())

        # #lbl-job-info contains Topic, "Limited (50 records)", format, and output file
        info_lbl = screen.query_one("#lbl-job-info", Static)
        info_text = str(info_lbl.render())
        assert "Kucing" in info_text
        assert "Limited (50 records)" in info_text
        assert "JSONL" in info_text.upper()
        assert "dataset_kucing" in info_text

        # #pbar (ProgressBar) total is 50
        pbar = screen.query_one("#pbar", ProgressBar)
        assert pbar.total == 50

        # #lbl-stage shows current stage
        stage_lbl = screen.query_one("#lbl-stage", Static)
        assert len(str(stage_lbl.render())) > 0

        # #lbl-stats shows counters (Completed, Generated, Failed)
        stats_lbl = screen.query_one("#lbl-stats", Static)
        stats_text = str(stats_lbl.render())
        assert "Completed" in stats_text
        assert "Generated" in stats_text
        assert "Failed" in stats_text


@pytest.mark.asyncio
async def test_progress_screen_display_unlimited():
    app = DatasetGeneratorApp()
    async with app.run_test(size=(80, 35)) as pilot:
        screen = ProgressScreen(
            topic="Kucing",
            is_limited=False,
            target_count=0,
            output_format="json",
            filename="unlimited_kucing",
        )
        await app.push_screen(screen)
        await pilot.pause()

        assert isinstance(app.screen, ProgressScreen)
        info_lbl = screen.query_one("#lbl-job-info", Static)
        info_text = str(info_lbl.render())
        assert "Unlimited Mode" in info_text


@pytest.mark.asyncio
async def test_progress_screen_stop_button():
    app = DatasetGeneratorApp()
    async with app.run_test(size=(80, 35)) as pilot:
        screen = ProgressScreen(
            topic="Deep Learning",
            is_limited=True,
            target_count=50,
        )
        await app.push_screen(screen)
        await pilot.pause()

        assert isinstance(app.screen, ProgressScreen)
        await pilot.click("#btn-stop")
        await pilot.pause()

        assert not isinstance(app.screen, ProgressScreen)


@pytest.mark.asyncio
async def test_progress_screen_key_bindings():
    app = DatasetGeneratorApp()
    async with app.run_test(size=(80, 35)) as pilot:
        # Test escape key
        screen1 = ProgressScreen(topic="Test Escape")
        await app.push_screen(screen1)
        await pilot.pause()
        assert app.screen is screen1

        await pilot.press("escape")
        await pilot.pause()
        assert app.screen is not screen1

        # Test ctrl+c key
        screen2 = ProgressScreen(topic="Test Ctrl+C")
        await app.push_screen(screen2)
        await pilot.pause()
        assert app.screen is screen2

        await pilot.press("ctrl+c")
        await pilot.pause()
        assert app.screen is not screen2
