# Task 8: End-to-End TUI Navigation Cycle Integration Test

**Files to create:**
- Create: `tests/e2e/__init__.py`
- Create: `tests/e2e/test_tui_flow.py`

**Instructions:**
1. Write the integration test in `tests/e2e/test_tui_flow.py`:
   - `test_full_tui_navigation_cycle`:
     - Initialize `ConfigManager` with a temporary config path (`tmp_path / "test_config.json"`).
     - Instantiate `DatasetGeneratorApp(config_manager=mgr)`.
     - Use `app.run_test()` and Pilot to simulate:
       1. Main menu loads, verify `btn-start` is disabled initially.
       2. Click `#btn-setup-q`, fill Base URL, API Key, Model ID, click `#btn-save`.
       3. Click `#btn-setup-a`, fill Base URL, API Key, Model ID, click `#btn-save`.
       4. Return to Main menu, verify both models show "Configured" and `#btn-start` is enabled.
       5. Click `#btn-view-config`, verify masked keys are shown, click `#btn-back`.
       6. Click `#btn-start`, fill topic "Kucing", select mode and format, click `#btn-start-job`.
       7. Verify `ProgressScreen` is active with topic "Kucing".
       8. Click `#btn-stop` (or press escape) to safely return to previous screen.
2. Run pytest: `python -m pytest tests/e2e/test_tui_flow.py -v`.
3. Run full test suite across the entire project to ensure 100% green tests.
4. Commit changes with: `git add . && git commit -m "test(e2e): add complete end-to-end tui navigation flow test"`.
5. Write brief report to `.superpowers/sdd/dual-model-dataset-generator/task-8-report.md`.
