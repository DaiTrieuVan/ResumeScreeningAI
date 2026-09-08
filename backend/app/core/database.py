from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

def _migrate_sqlite_columns(sync_conn):
    from sqlalchemy import text, inspect
    inspector = inspect(sync_conn)

    if "candidate_resumes" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("candidate_resumes")]
        if "job_id" not in columns:
            sync_conn.execute(text("ALTER TABLE candidate_resumes ADD COLUMN job_id VARCHAR(36)"))
        if "embedding_json" not in columns:
            sync_conn.execute(text("ALTER TABLE candidate_resumes ADD COLUMN embedding_json TEXT"))

    if "screening_results" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("screening_results")]
        if "skills_summary" not in columns:
            sync_conn.execute(text("ALTER TABLE screening_results ADD COLUMN skills_summary TEXT"))
        if "experience_summary" not in columns:
            sync_conn.execute(text("ALTER TABLE screening_results ADD COLUMN experience_summary TEXT"))
        if "education_summary" not in columns:
            sync_conn.execute(text("ALTER TABLE screening_results ADD COLUMN education_summary TEXT"))

async def init_db() -> None:
    # Import all models to ensure they are registered with Base.metadata before create_all
    import app.models.candidate_resume
    import app.models.job_posting
    import app.models.screening_result
    import app.models.gap_analysis
    import app.models.real_job
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_migrate_sqlite_columns)
