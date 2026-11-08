# Task 2: Root Entrypoint & Base Textual App Setup

**Files to modify/create:**
- Create: `main.py` (at repository root)
- Modify: `src/main.py`
- Create: `src/tui/__init__.py`
- Create: `src/tui/app.py`
- Create: `src/tui/styles.tcss`
- Create: `tests/test_entrypoint.py`

**Instructions:**
1. Write the tests in `tests/test_entrypoint.py` following TDD:
   - `test_main_import_and_execution`: Verifies `src.main.main()` runs `DatasetGeneratorApp.run()`.
   - `test_root_main_wrapper`: Verifies root `main.py` delegates to `src.main.main()`.
   - `test_app_initialization`: Verifies `DatasetGeneratorApp` instantiates with `ConfigManager` and loads `app.config`.
2. Run pytest to confirm failure.
3. Create `src/tui/__init__.py` (empty init).
4. Create `src/tui/styles.tcss` with clean dark theme styling.
5. Implement `src/tui/app.py` with `DatasetGeneratorApp(App)`:
   - Handles `CSS_PATH`, `TITLE = "Dual-Model Dataset Generator"`.
   - Accepts optional `config_manager: ConfigManager | None = None`.
   - Loads `self.config` from `self.config_manager.load_config()`.
   - If screens exist, mounts MainMenuScreen; if not yet available, mounts placeholder or header.
6. Modify `src/main.py` to instantiate and run `DatasetGeneratorApp`.
7. Create root `main.py` with `sys.path.insert(0, ...)` and call `src.main.main()`.
8. Run pytest: `python -m pytest tests/test_entrypoint.py -v` and ensure all tests pass.
9. Commit all changes with `git add . && git commit -m "feat(tui): setup root entrypoint and base textual app"`.
10. Save brief summary report to `.superpowers/sdd/dual-model-dataset-generator/task-2-report.md`.
