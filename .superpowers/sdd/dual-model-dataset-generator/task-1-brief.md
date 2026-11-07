# Task 1: Pydantic Configuration Schema & Config Manager

**Files to modify/create:**
- Modify: `src/config/schema.py`
- Create: `src/config/config_manager.py`
- Create: `tests/test_config_manager.py`

**Instructions:**
1. Write the tests in `tests/test_config_manager.py` following TDD:
   - `test_default_config_creation`: Verifies default AppConfig when file does not exist.
   - `test_save_and_load_model_config`: Verifies saving ModelConfig for question_model and reading it back.
   - `test_masked_api_key`: Verifies `masked_api_key` property hides secret except prefix and suffix (e.g. `sk-1234...cdef`), or `********` if short.
2. Run pytest to confirm failure.
3. Update `src/config/schema.py` with `ModelConfig`, `PreferencesConfig`, `AppConfig`.
4. Implement `src/config/config_manager.py` with atomic write, chmod 0o600 on unix, and save/load logic.
5. Run pytest: `python -m pytest tests/test_config_manager.py -v` and ensure all tests pass.
6. Commit changes with message: `feat(config): implement pydantic schema and config manager`
7. Save brief summary report to `.superpowers/sdd/dual-model-dataset-generator/task-1-report.md` with format:
   - Status: DONE
   - Commit: <commit-hash>
   - Tests: <summary of pytest output>
   - Concerns: <any concerns or None>
