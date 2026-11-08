from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.config.schema import ModelConfig
from src.generation.pipeline import (
    GenerationPipeline,
    append_record,
    clean_json_response,
    extract_questions_fallback,
)


def test_clean_json_response():
    raw = "```json\n{\"questions\": [{\"question\": \"Test?\"}]}\n```"
    assert clean_json_response(raw) == '{"questions": [{"question": "Test?"}]}'


def test_extract_questions_fallback():
    raw = "1. What is machine learning?\n2. How does gradient descent work?\nSome explanation"
    extracted = extract_questions_fallback(raw)
    assert len(extracted) == 2
    assert extracted[0] == "What is machine learning?"
    assert extracted[1] == "How does gradient descent work?"


def test_append_record_jsonl(tmp_path: Path):
    rec = {"id": 1, "topic": "AI", "question": "Q1", "answer": "A1", "status": "completed", "created_at": "2026-01-01"}
    out_file = append_record(tmp_path, "test_dataset", "jsonl", rec)
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8").strip()
    data = json.loads(content)
    assert data["question"] == "Q1"


def test_append_record_csv(tmp_path: Path):
    rec = {"id": 1, "topic": "AI", "question": "Q1", "answer": "A1", "status": "completed", "created_at": "2026-01-01"}
    out_file = append_record(tmp_path, "test_dataset", "csv", rec)
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "question,answer" in content
    assert "Q1,A1" in content


def test_generation_pipeline_mock(tmp_path: Path):
    q_cfg = ModelConfig(base_url="https://fake.url/v1", api_key="sk-test", model="gpt-4o")
    a_cfg = ModelConfig(base_url="https://fake.url/v1", api_key="sk-test", model="gpt-4o")
    pipeline = GenerationPipeline(q_cfg, a_cfg)

    with patch("httpx.Client.post") as mock_post:
        # Mock Question response
        mock_resp_q = MagicMock()
        mock_resp_q.status_code = 200
        mock_resp_q.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"questions": [{"question": "What is Python?"}]}'
                    }
                }
            ]
        }
        # Mock Answer response
        mock_resp_a = MagicMock()
        mock_resp_a.status_code = 200
        mock_resp_a.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Python is a high-level programming language."
                    }
                }
            ]
        }

        mock_post.side_effect = [mock_resp_q, mock_resp_a]

        questions = pipeline.generate_questions_batch("Python", count=1)
        assert len(questions) == 1
        assert questions[0] == "What is Python?"

        answer = pipeline.generate_answer("Python", questions[0])
        assert "high-level programming language" in answer
