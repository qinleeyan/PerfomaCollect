# Task 3: Main Menu Screen & Live Model Status Badges

**Files to modify/create:**
- Create: `src/tui/screens/__init__.py`
- Create: `src/tui/screens/main_menu.py`
- Create: `tests/test_main_menu.py`

**Instructions:**
1. Write the tests in `tests/test_main_menu.py`:
   - `test_main_menu_initial_status`: Start `DatasetGeneratorApp`, verify MainMenuScreen is mounted, question and answer models show "Not Configured", Start button is disabled.
   - `test_main_menu_with_models_configured`: Start `DatasetGeneratorApp` with both models configured in `app.config`, verify statuses show model names with "Configured" and Start button is enabled.
2. Run pytest to see it fail.
3. Create `src/tui/screens/__init__.py`.
4. Implement `src/tui/screens/main_menu.py`:
   - Extends Textual `Screen`.
   - Layout:
     - Header
     - Form container:
       - Header card Static: "DUAL-MODEL DATASET GENERATOR"
       - Model status badges: `#status-question` and `#status-answer`
       - Action buttons:
         - `[1] Setup Question Model` (`#btn-setup-q`)
         - `[2] Setup Answer Model` (`#btn-setup-a`)
         - `[3] Start Dataset Generation` (`#btn-start`, disabled if not both configured)
         - `[4] View Current Configuration` (`#btn-view-config`)
         - `[5] Exit` (`#btn-exit`, calls `self.app.exit()`)
     - Footer
   - `update_model_statuses()` method to dynamically update labels and toggle `#btn-start.disabled`.
   - `on_mount` calls `update_model_statuses()`.
   - Button press handlers for exit and stubs/screen pushes.
5. Run pytest: `python -m pytest tests/test_main_menu.py -v`.
6. Run full pytest to verify no regressions.
7. Commit changes with: `git add . && git commit -m "feat(tui): implement main menu screen and status badges"`.
8. Write brief report to `.superpowers/sdd/dual-model-dataset-generator/task-3-report.md`.
