# Task 6: Generation Setup Screen (Topic, Target, Format)

**Files to modify/create:**
- Create: `src/tui/screens/generation_setup.py`
- Create: `tests/test_generation_setup.py`

**Instructions:**
1. Write the tests in `tests/test_generation_setup.py`:
   - `test_generation_setup_empty_topic_validation`: Submitting without topic shows error message and does not proceed.
   - `test_generation_setup_target_count_validation`: If mode is Limited and target count is <= 0 or non-integer, shows error message and does not proceed.
   - `test_generation_setup_cancel_button`: Clicking Cancel pops the screen.
   - `test_generation_setup_submit_valid`: Filling topic, valid target count, format selection, and clicking Start Generation transitions (pushes ProgressScreen or fires event).
2. Run pytest to see it fail.
3. Implement `src/tui/screens/generation_setup.py`:
   - Extends Textual `Screen`.
   - Header with `NEW DATASET GENERATION`.
   - Fields:
     - Topic input (`#input-topic`)
     - RadioSet (`#radio-mode`) with RadioButtons: "Limited (Specify target records)" (`#mode-limited`, value=True) and "Unlimited (Continue until stopped)" (`#mode-unlimited`)
     - Target count input (`#input-target`, default="50", type="integer")
     - Format selector (`#select-format`, Select widget with options: [("JSON Lines (.jsonl)", "jsonl"), ("JSON Array (.json)", "json"), ("CSV (.csv)", "csv"), ("Excel (.xlsx)", "xlsx")], default="jsonl")
     - Output filename input (`#input-filename`, default="dataset_output")
     - Error label (`#error-label`)
     - Action buttons: "Start Generation" (`#btn-start-job`, variant="success") and "Cancel" (`#btn-cancel`, variant="error")
   - Handlers:
     - `#btn-cancel`: pops screen.
     - `#btn-start-job`: validates topic is non-empty; if limited mode validates target > 0; then pushes `ProgressScreen(topic=..., is_limited=..., target_count=..., output_format=..., filename=...)` (handles safe import/mock if progress screen not yet ready).
   - Export in `src/tui/screens/__init__.py`.
4. Run pytest: `python -m pytest tests/test_generation_setup.py -v`.
5. Run full pytest to verify no regressions.
6. Commit changes with: `git add . && git commit -m "feat(tui): implement generation setup screen"`.
7. Write brief report to `.superpowers/sdd/dual-model-dataset-generator/task-6-report.md`.
