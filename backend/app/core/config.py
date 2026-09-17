# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Resume Screening AI"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "sqlite+aiosqlite:///./resume_screening.db"
    STORAGE_DIR: str = os.path.abspath("./storage/resumes")
    GEMINI_API_KEY: str = ""
    DEFAULT_EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    DEFAULT_LLM_MODEL: str = "gemini-3.6-flash"
    RECRUITER_WORKSPACE_V2_ENABLED: bool = True
    OFFLINE_MODE: bool = False
    OFFLINE_ENGINE: str = "deterministic-keyword-v1"
    MAX_BATCH_FILES: int = 200
    MAX_UPLOAD_FILE_BYTES: int = 15 * 1024 * 1024
    UPLOAD_MAX_ATTEMPTS: int = 3
    PROCESSING_LEASE_SECONDS: int = 120
    IDEMPOTENCY_TTL_HOURS: int = 24
    DEFAULT_REVIEW_PRIVACY_MODE: str = "IDENTIFIED"
    EVALUATION_DATASET_DIR: str = os.path.abspath("./evaluation/datasets")
    BENCHMARK_ARTIFACT_DIR: str = os.path.abspath("./artifacts/benchmark")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

os.makedirs(settings.STORAGE_DIR, exist_ok=True)
