import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class JobPosting(Base):
    __tablename__ = "job_postings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(255), nullable=True)
    required_skills: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    preferred_skills: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    min_years_experience: Mapped[int] = mapped_column(Integer, default=0)
    required_education: Mapped[str] = mapped_column(String(255), nullable=True)
    weight_skills: Mapped[float] = mapped_column(Float, default=0.50)
    weight_experience: Mapped[float] = mapped_column(Float, default=0.35)
    weight_education: Mapped[float] = mapped_column(Float, default=0.15)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    active_criteria_set_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    screenings = relationship("ScreeningResult", back_populates="job", cascade="all, delete-orphan")
