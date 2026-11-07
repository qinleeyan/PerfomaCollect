from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    base_url: str
    api_key: str
    model: str

    @property
    def masked_api_key(self) -> str:
        if not self.api_key or len(self.api_key) <= 8:
            return "********"
        return f"{self.api_key[:7]}...{self.api_key[-4:]}"


class PreferencesConfig(BaseModel):
    default_output_format: str = "jsonl"
    default_output_directory: str = "./output"


class AppConfig(BaseModel):
    version: int = 1
    question_model: Optional[ModelConfig] = None
    answer_model: Optional[ModelConfig] = None
    preferences: PreferencesConfig = Field(default_factory=PreferencesConfig)


class Settings(BaseModel):
    pass
