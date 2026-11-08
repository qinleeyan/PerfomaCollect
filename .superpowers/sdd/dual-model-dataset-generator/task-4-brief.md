# Task 4: Model Setup Screen (Question & Answer Model Forms)

**Files to modify/create:**
- Create: `src/tui/screens/model_setup.py`
- Create: `tests/test_model_setup.py`

**Instructions:**
1. Write the tests in `tests/test_model_setup.py`:
   - `test_model_setup_prepopulation`: When target model is already in app.config, form inputs are pre-populated with existing base_url, api_key, model.
   - `test_model_setup_save_flow`: Entering valid Base URL, API Key, and Model ID and clicking Save saves the ModelConfig into app.config and calls config_manager.save_model_config, then pops the screen.
   - `test_model_setup_validation`: Submitting with empty fields displays an error label and does not pop the screen.
   - `test_model_setup_cancel`: Clicking Cancel pops the screen without changing app.config.
   - `test_model_setup_test_connection_click`: Clicking "Test Connection" validates non-empty inputs and provides immediate UI feedback.
2. Run pytest to see it fail.
3. Implement `src/tui/screens/model_setup.py`:
   - Extends Textual `Screen`.
   - Constructor accepts `target: str` ("question_model" or "answer_model").
   - Header with `f"SETUP {self.target_name.upper()}"`.
   - Form fields:
     - `Base URL` Input (`#input-base-url`)
     - `API Key` Input (`#input-api-key`, `password=True`)
     - `Model ID` Input (`#input-model-id`)
     - Result label (`#test-result-label`)
   - Buttons:
     - `Test Connection` (`#btn-test`, variant="default")
     - `Save Configuration` (`#btn-save`, variant="success")
     - `Cancel` (`#btn-cancel`, variant="error")
   - `on_mount`: pre-populate inputs if `app.config.<target>` exists.
   - `on_button_pressed`:
     - `#btn-cancel`: pops screen.
     - `#btn-test`: validates fields, updates `#test-result-label`.
     - `#btn-save`: validates fields, creates `ModelConfig`, calls `app.config_manager.save_model_config(self.target, model)`, updates `app.config`, refreshes parent screen status if needed, pops screen.
4. Run pytest: `python -m pytest tests/test_model_setup.py -v`.
5. Run full pytest to verify no regressions.
6. Commit changes with: `git add . && git commit -m "feat(tui): implement model setup form screen"`.
7. Write brief report to `.superpowers/sdd/dual-model-dataset-generator/task-4-report.md`.
