from collections.abc import Callable

from sqlalchemy import Connection, inspect, text


Migration = tuple[str, Callable[[Connection], None]]


def _columns(connection: Connection, table: str) -> set[str]:
    inspector = inspect(connection)
    if table not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table)}


def _add_column(connection: Connection, table: str, name: str, ddl: str) -> None:
    if name not in _columns(connection, table):
        connection.execute(text(f'ALTER TABLE "{table}" ADD COLUMN "{name}" {ddl}'))


def _migration_001_legacy_columns(connection: Connection) -> None:
    _add_column(connection, "candidate_resumes", "job_id", "VARCHAR(36)")
    _add_column(connection, "candidate_resumes", "embedding_json", "TEXT")
    _add_column(connection, "screening_results", "skills_summary", "TEXT")
    _add_column(connection, "screening_results", "experience_summary", "TEXT")
    _add_column(connection, "screening_results", "education_summary", "TEXT")


def _migration_002_recruiter_versioning(connection: Connection) -> None:
    _add_column(connection, "job_postings", "active_criteria_set_id", "VARCHAR(36)")
    _add_column(connection, "job_postings", "version", "INTEGER NOT NULL DEFAULT 1")
    _add_column(connection, "screening_results", "criteria_set_id", "VARCHAR(36)")
    _add_column(connection, "screening_results", "evaluation_kind", "VARCHAR(20) NOT NULL DEFAULT 'LEGACY'")


def _migration_003_recruiter_query_indexes(connection: Connection) -> None:
    if {"job_id", "overall_score"} <= _columns(connection, "screening_results"):
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_screening_result_job_score ON screening_results(job_id, overall_score)"))
    if {"job_id", "uploaded_at"} <= _columns(connection, "candidate_resumes"):
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_resume_job_uploaded ON candidate_resumes(job_id, uploaded_at)"))


MIGRATIONS: list[Migration] = [
    ("001_legacy_columns", _migration_001_legacy_columns),
    ("002_recruiter_versioning", _migration_002_recruiter_versioning),
    ("003_recruiter_query_indexes", _migration_003_recruiter_query_indexes),
]


def run_migrations(connection: Connection) -> None:
    """Run additive schema upgrades once and record each successful version."""

    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(100) PRIMARY KEY,
                applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )
    applied = {
        row[0]
        for row in connection.execute(text("SELECT version FROM schema_migrations"))
    }
    for version, migration in MIGRATIONS:
        if version in applied:
            continue
        migration(connection)
        connection.execute(
            text("INSERT INTO schema_migrations(version) VALUES (:version)"),
            {"version": version},
        )
