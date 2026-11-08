# Task 7: Generation Progress Screen & Graceful Exit

**Files to modify/create:**
- Create: `src/tui/screens/progress.py`
- Create: `tests/test_progress.py`

**Instructions:**
1. Write the tests in `tests/test_progress.py`:
   - `test_progress_screen_display_limited`: Mount ProgressScreen with is_limited=True, target_count=50. Verify:
     - Header card "GENERATION IN PROGRESS" is rendered.
     - `#lbl-job-info` contains Topic, "Limited (50 records)", format, and output file.
     - `#pbar` (ProgressBar) total is 50.
     - `#lbl-stage` shows current stage.
     - `#lbl-stats` shows counters (Completed, Generated, Failed).
   - `test_progress_screen_display_unlimited`: Mount ProgressScreen with is_limited=False. Verify `#lbl-job-info` displays "Unlimited Mode".
   - `test_progress_screen_stop_button`: Clicking "#btn-stop" pops the screen safely.
   - `test_progress_screen_key_bindings`: Pressing "escape" or "ctrl+c" triggers `action_stop_job()` and pops the screen.
2. Run pytest to see it fail.
3. Implement `src/tui/screens/progress.py`:
   - Extends Textual `Screen`.
   - BINDINGS = [("escape", "stop_job", "Stop"), ("ctrl+c", "stop_job", "Stop")].
   - Constructor parameters:
     - `topic: str`
     - `is_limited: bool = True`
     - `target_count: int = 50`
     - `output_format: str = "jsonl"`
     - `filename: str = "dataset_output"`
   - Layout:
     - Header
     - Form container:
       - Header card Static: "GENERATION IN PROGRESS"
       - Job info label (`#lbl-job-info`)
       - Stage indicator (`#lbl-stage`)
       - ProgressBar (`#pbar`, total=target_count if is_limited else 100, show_eta=False)
       - Stats label (`#lbl-stats`)
       - Help notice: "Press Ctrl+C or Escape to stop safely."
       - Button "Stop Generation" (`#btn-stop`, variant="error")
     - Footer
   - `action_stop_job()`: pops screen safely.
   - `on_button_pressed()`: handles `#btn-stop`.
   - Export in `src/tui/screens/__init__.py`.
4. Run pytest: `python -m pytest tests/test_progress.py -v`.
5. Run full pytest to verify no regressions.
6. Commit changes with: `git add . && git commit -m "feat(tui): implement progress screen with graceful exit bindings"`.
7. Write brief report to `.superpowers/sdd/dual-model-dataset-generator/task-7-report.md`.
