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
    DEFAULT_LLM_MODEL: str = "gemini-1.5-flash"
    RECRUITER_WORKSPACE_V2_ENABLED: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

os.makedirs(settings.STORAGE_DIR, exist_ok=True)
