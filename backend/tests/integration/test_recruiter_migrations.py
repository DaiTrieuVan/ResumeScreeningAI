# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import sqlite3

from sqlalchemy import create_engine, inspect

from app.core.migrations import MIGRATIONS, run_migrations


def test_migration_runner_is_idempotent(tmp_path):
    database_path = tmp_path / "legacy.db"
    raw = sqlite3.connect(database_path)
    raw.executescript(
        """
        CREATE TABLE job_postings (id VARCHAR(36) PRIMARY KEY);
        CREATE TABLE candidate_resumes (id VARCHAR(36) PRIMARY KEY);
        CREATE TABLE screening_results (id VARCHAR(36) PRIMARY KEY);
        """
    )
    raw.close()

    engine = create_engine(f"sqlite:///{database_path}")
    with engine.begin() as connection:
        run_migrations(connection)
        run_migrations(connection)

    inspector = inspect(engine)
    job_columns = {column["name"] for column in inspector.get_columns("job_postings")}
    result_columns = {column["name"] for column in inspector.get_columns("screening_results")}

    assert {"active_criteria_set_id", "version"} <= job_columns
    assert {"criteria_set_id", "evaluation_kind"} <= result_columns

    with engine.connect() as connection:
        applied = connection.exec_driver_sql(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).scalars().all()

    assert applied == [version for version, _ in MIGRATIONS]
