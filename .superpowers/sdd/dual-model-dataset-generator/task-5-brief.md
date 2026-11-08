# Task 5: View Configuration Screen

**Files to modify/create:**
- Create: `src/tui/screens/view_config.py`
- Create: `tests/test_view_config.py`

**Instructions:**
1. Write the tests in `tests/test_view_config.py`:
   - `test_view_config_display_with_configured_models`: Set up an AppConfig with question_model, answer_model, and preferences. Mount ViewConfigScreen, verify:
     - Question Model base_url, model name, and masked API key are rendered.
     - Answer Model base_url, model name, and masked API key are rendered.
     - Unmasked raw API key NEVER appears anywhere in the rendered output.
     - Preferences default_output_format and default_output_directory are rendered.
   - `test_view_config_display_unconfigured`: When models are None, displays "Not Configured".
   - `test_view_config_back_button`: Clicking "#btn-back" pops the screen.
2. Run pytest to see it fail.
3. Implement `src/tui/screens/view_config.py`:
   - Extends Textual `Screen`.
   - Header with `CURRENT CONFIGURATION`.
   - Static `#config-details` rendering formatted information:
     - Question Model: Base URL, Model ID, API Key (always using `masked_api_key`)
     - Answer Model: Base URL, Model ID, API Key (always using `masked_api_key`)
     - Preferences: Default format, Default directory
   - Button `#btn-back` (variant="primary") to pop the screen.
   - Add export in `src/tui/screens/__init__.py`.
4. Run pytest: `python -m pytest tests/test_view_config.py -v`.
5. Run full pytest to verify no regressions.
6. Commit changes with: `git add . && git commit -m "feat(tui): implement view configuration screen with redacted credentials"`.
7. Write brief report to `.superpowers/sdd/dual-model-dataset-generator/task-5-report.md`.
