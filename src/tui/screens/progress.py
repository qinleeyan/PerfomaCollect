from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, ProgressBar, RichLog, Static

from src.generation.pipeline import GenerationPipeline, append_record


class ProgressScreen(Screen):
    BINDINGS = [("escape", "stop_job", "Stop"), ("ctrl+c", "stop_job", "Stop")]

    def __init__(
        self,
        topic: str,
        is_limited: bool = True,
        target_count: int = 50,
        output_format: str = "jsonl",
        filename: str = "dataset_output",
        output_dir: Optional[Path] = None,
    ) -> None:
        super().__init__()
        self.topic = topic
        self.is_limited = is_limited
        self.target_count = target_count
        self.output_format = output_format
        self.filename = filename
        self.output_dir = output_dir or Path("output")

        self.is_stopped = False
        self.is_done = False
        self.records_completed = 0
        self.questions_generated = 0
        self.failed_count = 0
        self.all_questions: List[str] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="form-container"):
            yield Static("GENERATION IN PROGRESS", id="header-card")
            mode_str = f"Limited ({self.target_count} records)" if self.is_limited else "Unlimited Mode"
            info = (
                f"Topic: [bold]{self.topic}[/bold] | Mode: {mode_str} | "
                f"Format: {self.output_format.upper()} | File: {self.filename}.{self.output_format}"
            )
            yield Static(info, id="lbl-job-info")
            yield Static("Current Stage: [yellow]Ready / Standing By[/yellow]", id="lbl-stage")
            yield ProgressBar(
                total=self.target_count if self.is_limited else 100,
                show_eta=False,
                id="pbar",
            )
            yield Static("Records Completed: 0 | Questions Generated: 0 | Failed: 0", id="lbl-stats")

            with Horizontal(id="split-container"):
                with Vertical(classes="log-column"):
                    yield Static("❓ QUESTIONS GENERATED", classes="column-header", id="header-questions")
                    yield RichLog(id="log-questions", wrap=True, markup=True)
                with Vertical(classes="log-column"):
                    yield Static("💡 ANSWERS COMPLETED", classes="column-header", id="header-answers")
                    yield RichLog(id="log-answers", wrap=True, markup=True)

            yield Static("Press [bold red]Ctrl+C[/bold red] or [bold]Escape[/bold] to stop safely.", classes="form-label")
            with Vertical():
                yield Button("Stop Generation", id="btn-stop", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self.start_generation_worker()

    def _update_stage(self, message: str) -> None:
        try:
            self.query_one("#lbl-stage", Static).update(f"Current Stage: {message}")
        except Exception:
            pass

    def _update_stats(self) -> None:
        try:
            self.query_one("#lbl-stats", Static).update(
                f"Records Completed: {self.records_completed} | "
                f"Questions Generated: {self.questions_generated} | "
                f"Failed: {self.failed_count}"
            )
            self.query_one("#header-questions", Static).update(f"❓ QUESTIONS ({self.questions_generated})")
            self.query_one("#header-answers", Static).update(f"💡 ANSWERS ({self.records_completed})")
        except Exception:
            pass

    def _log_question(self, text: str) -> None:
        try:
            self.query_one("#log-questions", RichLog).write(text)
        except Exception:
            pass

    def _log_answer(self, text: str) -> None:
        try:
            self.query_one("#log-answers", RichLog).write(text)
        except Exception:
            pass

    def _advance_progress(self, amount: int = 1) -> None:
        try:
            self.query_one("#pbar", ProgressBar).advance(amount)
        except Exception:
            pass

    def _finish_ui(self, message: str) -> None:
        try:
            self.query_one("#lbl-stage", Static).update(f"Current Stage: {message}")
            btn = self.query_one("#btn-stop", Button)
            btn.label = "Back to Menu"
            btn.variant = "primary"
        except Exception:
            pass

    def _safe_call(self, fn, *args) -> None:
        try:
            if hasattr(self, "app") and self.app:
                self.app.call_from_thread(fn, *args)
        except Exception:
            pass

    @work(exclusive=True, thread=True)
    def start_generation_worker(self) -> None:
        app_cfg = getattr(self.app, "config", None)
        q_model = getattr(app_cfg, "question_model", None) if app_cfg else None
        a_model = getattr(app_cfg, "answer_model", None) if app_cfg else None

        if not q_model or not a_model:
            self._safe_call(
                self._update_stage,
                "[yellow]Standing By (Models not fully configured)[/yellow]",
            )
            return

        pipeline = GenerationPipeline(q_model, a_model)
        self._safe_call(self._update_stage, "[cyan]Starting generation pipeline...[/cyan]")

        batch_num = 1
        q_counter = 0

        while not self.is_stopped:
            if self.is_limited and self.records_completed >= self.target_count:
                self.is_done = True
                self._safe_call(
                    self._finish_ui,
                    f"[green]Completed! Generated {self.records_completed} records in output/{self.filename}.{self.output_format}[/green]",
                )
                break

            # Calculate batch size
            if self.is_limited:
                remaining = self.target_count - self.records_completed
                batch_size = min(5, remaining)
            else:
                batch_size = 5

            self._safe_call(
                self._update_stage,
                f"[yellow]Generating {batch_size} questions (Batch {batch_num})...[/yellow]",
            )

            try:
                questions = pipeline.generate_questions_batch(
                    self.topic, count=batch_size, existing_questions=self.all_questions
                )
                self.questions_generated += len(questions)
                self.all_questions.extend(questions)

                # Log each newly generated question
                for q in questions:
                    q_counter += 1
                    self._safe_call(
                        self._log_question,
                        f"[bold cyan]{q_counter}.[/bold cyan] {q}\n",
                    )

                self._safe_call(self._update_stats)
            except Exception as e:
                self.failed_count += 1
                self._safe_call(self._update_stats)
                err_msg = str(e)
                if len(err_msg) > 120:
                    err_msg = err_msg[:120] + "..."
                self._safe_call(
                    self._update_stage,
                    f"[red]Question Error: {err_msg}[/red]",
                )
                self._safe_call(
                    self._log_question,
                    f"[bold red][ERROR Batch {batch_num}][/bold red] {err_msg}\n",
                )
                # Sleep briefly before retry, check if stopped
                for _ in range(5):
                    if self.is_stopped:
                        break
                    time.sleep(0.5)
                continue

            # Answer each question one by one
            for idx, q in enumerate(questions, 1):
                if self.is_stopped:
                    break

                q_num = self.records_completed + 1
                q_preview = q if len(q) <= 40 else q[:37] + "..."
                self._safe_call(
                    self._update_stage,
                    f"[cyan]Answering ({q_num}): \"{q_preview}\"...[/cyan]",
                )

                try:
                    ans = pipeline.generate_answer(self.topic, q)
                    record = {
                        "id": q_num,
                        "topic": self.topic,
                        "question": q,
                        "answer": ans,
                        "status": "completed",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                    append_record(self.output_dir, self.filename, self.output_format, record)
                    self.records_completed += 1

                    # Log answer in right panel
                    self._safe_call(
                        self._log_answer,
                        f"[bold green]{q_num}.[/bold green] {ans}\n",
                    )
                    self._safe_call(self._advance_progress, 1)
                    self._safe_call(self._update_stats)
                except Exception as e:
                    self.failed_count += 1
                    self._safe_call(self._update_stats)
                    err_msg = str(e)
                    if len(err_msg) > 120:
                        err_msg = err_msg[:120] + "..."
                    self._safe_call(
                        self._update_stage,
                        f"[red]Answer Error: {err_msg}[/red]",
                    )
                    self._safe_call(
                        self._log_answer,
                        f"[bold red]{q_num}. [FAILED][/bold red] {err_msg}\n",
                    )
                    fail_record = {
                        "id": q_num,
                        "topic": self.topic,
                        "question": q,
                        "answer": "",
                        "status": "answer_failed",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                    append_record(self.output_dir, self.filename, self.output_format, fail_record)

                if self.is_limited and self.records_completed >= self.target_count:
                    break

            batch_num += 1

        if self.is_stopped and not self.is_done:
            self._safe_call(
                self._finish_ui,
                f"[yellow]Stopped by user. {self.records_completed} records saved in output/{self.filename}.{self.output_format}[/yellow]",
            )

    def action_stop_job(self) -> None:
        if not self.is_stopped and not self.is_done:
            self.is_stopped = True
            self._update_stage("[yellow]Stopping gracefully...[/yellow]")
        else:
            self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-stop":
            if self.is_done or self.is_stopped:
                self.app.pop_screen()
            else:
                self.action_stop_job()
