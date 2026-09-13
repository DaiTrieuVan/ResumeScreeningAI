# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class CandidateResume(Base):
    __tablename__ = "candidate_resumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=True)
    parsed_name: Mapped[str] = mapped_column(String(255), nullable=True)
    parsed_email: Mapped[str] = mapped_column(String(255), nullable=True)
    parsed_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    extracted_skills: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    work_history: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    education: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    parse_status: Mapped[str] = mapped_column(String(50), default="SUCCESS")
    parse_error_message: Mapped[str] = mapped_column(Text, nullable=True)
    embedding_json: Mapped[str] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    screenings = relationship("ScreeningResult", back_populates="resume", cascade="all, delete-orphan")
