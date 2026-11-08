from __future__ import annotations

import csv
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Generator, List, Optional
import httpx

from src.config.schema import ModelConfig


def clean_json_response(content: str) -> str:
    """Strip markdown code fences and whitespace from response."""
    content = content.strip()
    # Remove markdown code block fences if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content, re.IGNORECASE)
    if match:
        content = match.group(1).strip()
    return content


def extract_questions_fallback(raw_text: str) -> List[str]:
    """Fallback extraction when response is not strictly valid JSON."""
    questions: List[str] = []
    lines = raw_text.strip().splitlines()
    for line in lines:
        line = line.strip()
        is_numbered = bool(re.match(r"^(\d+[\.\)]|\*|-)\s*", line))
        cleaned = re.sub(r"^(\d+[\.\)]|\*|-)\s*", "", line).strip()
        cleaned = cleaned.strip("\"'").strip()
        if cleaned and (cleaned.endswith("?") or (is_numbered and len(cleaned) > 5)):
            questions.append(cleaned)
    return questions


class GenerationPipeline:
    def __init__(
        self,
        question_model: ModelConfig,
        answer_model: ModelConfig,
        timeout: float = 60.0,
    ) -> None:
        self.question_model = question_model
        self.answer_model = answer_model
        self.timeout = timeout

    def generate_questions_batch(
        self,
        topic: str,
        count: int = 5,
        existing_questions: Optional[List[str]] = None,
    ) -> List[str]:
        """Request a batch of questions from Question Model."""
        system_prompt = (
            "You are a question-generation model.\n"
            "Your only task is to generate clear, useful, and diverse questions "
            "based on the topic provided by the user.\n"
            "Rules:\n"
            "- Generate questions only.\n"
            "- Do not answer any question.\n"
            "- Do not include explanations.\n"
            "- Avoid duplicate or near-duplicate questions.\n"
            "- Return valid structured JSON matching the requested schema."
        )

        user_content = (
            f"Topic: {topic}\n"
            f"Generate {count} diverse questions about this topic.\n\n"
            "Return valid JSON strictly matching this structure:\n"
            '{\n  "questions": [\n    {"question": "..."}\n  ]\n}'
        )

        if existing_questions:
            recent_sample = existing_questions[-10:]
            user_content += (
                "\n\nDo not repeat or closely rephrase any of these already generated questions:\n"
                + "\n".join(f"- {q}" for q in recent_sample)
            )

        url = f"{self.question_model.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.question_model.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.question_model.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "stream": False,
        }

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(
                    f"Question Model HTTP {resp.status_code}: {resp.text[:300]}"
                )
            data = resp.json()

        raw_content = data["choices"][0]["message"]["content"]
        cleaned = clean_json_response(raw_content)

        questions: List[str] = []
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict) and "questions" in parsed:
                for item in parsed["questions"]:
                    if isinstance(item, dict) and "question" in item:
                        q_str = str(item["question"]).strip()
                        if q_str:
                            questions.append(q_str)
                    elif isinstance(item, str) and item.strip():
                        questions.append(item.strip())
            elif isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, str) and item.strip():
                        questions.append(item.strip())
                    elif isinstance(item, dict) and "question" in item:
                        questions.append(str(item["question"]).strip())
        except Exception:
            # Fallback regex search for {"question": "..."}
            matches = re.findall(r'"question"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', cleaned)
            if matches:
                questions = [m.replace('\\"', '"').strip() for m in matches if m.strip()]
            else:
                questions = extract_questions_fallback(raw_content)

        if not questions:
            raise ValueError(f"No questions could be extracted from: {raw_content[:200]}")

        return questions[:count]

    def generate_answer(self, topic: str, question: str) -> str:
        """Request answer for a single question from Answer Model."""
        system_prompt = (
            "You are an answer-generation model.\n"
            "Your only task is to answer the user's question accurately and clearly.\n"
            "Rules:\n"
            "- Answer the given question directly.\n"
            "- Do not generate additional questions.\n"
            "- Do not change the original question.\n"
            "- If the answer is uncertain, state the uncertainty.\n"
            "- Return plain text."
        )

        user_content = (
            f"Topic context: {topic}\n\n"
            f"Question:\n{question}\n\n"
            "Provide a clear and informative answer."
        )

        url = f"{self.answer_model.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.answer_model.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.answer_model.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "stream": False,
        }

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(
                    f"Answer Model HTTP {resp.status_code}: {resp.text[:300]}"
                )
            data = resp.json()

        answer = data["choices"][0]["message"]["content"].strip()
        return answer


def append_record(
    output_dir: Path,
    filename: str,
    output_format: str,
    record: dict[str, Any],
) -> Path:
    """Save record immediately to disk in specified format."""
    output_dir.mkdir(parents=True, exist_ok=True)
    fmt = output_format.lower().lstrip(".")
    out_file = output_dir / f"{filename}.{fmt}"

    if fmt == "jsonl":
        with open(out_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    elif fmt == "json":
        # Incremental JSON array update
        records = []
        if out_file.exists():
            try:
                with open(out_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
                if not isinstance(records, list):
                    records = []
            except Exception:
                records = []
        records.append(record)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

    elif fmt == "csv":
        file_exists = out_file.exists()
        fields = ["id", "topic", "question", "answer", "status", "created_at"]
        with open(out_file, "a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            if not file_exists:
                writer.writeheader()
            writer.writerow({k: record.get(k, "") for k in fields})

    elif fmt == "xlsx":
        try:
            import openpyxl

            if out_file.exists():
                wb = openpyxl.load_workbook(out_file)
                ws = wb.active
            else:
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Dataset"
                ws.append(["id", "topic", "question", "answer", "status", "created_at"])

            ws.append([
                record.get("id"),
                record.get("topic"),
                record.get("question"),
                record.get("answer"),
                record.get("status"),
                record.get("created_at"),
            ])
            wb.save(out_file)
        except ImportError:
            # Fallback to jsonl if openpyxl not available
            fallback = output_dir / f"{filename}.jsonl"
            with open(fallback, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            return fallback

    return out_file
