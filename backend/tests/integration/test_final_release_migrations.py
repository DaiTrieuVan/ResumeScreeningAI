# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import sqlite3

from sqlalchemy import create_engine, inspect

from app.core.migrations import run_migrations


def test_final_release_additive_columns_are_idempotent(tmp_path):
    database_path = tmp_path / "legacy-final-release.db"
    raw = sqlite3.connect(database_path)
    raw.executescript(
        """
        CREATE TABLE candidate_applications (id VARCHAR(36) PRIMARY KEY);
        CREATE TABLE evidence_snippets (id VARCHAR(36) PRIMARY KEY);
        CREATE TABLE upload_items (id VARCHAR(36) PRIMARY KEY);
        """
    )
    raw.close()

    engine = create_engine(f"sqlite:///{database_path}")
    with engine.begin() as connection:
        run_migrations(connection)
        run_migrations(connection)

    inspector = inspect(engine)
    application_columns = {column["name"] for column in inspector.get_columns("candidate_applications")}
    evidence_columns = {column["name"] for column in inspector.get_columns("evidence_snippets")}
    upload_columns = {column["name"] for column in inspector.get_columns("upload_items")}

    assert {"evaluation_stale", "stale_reason"} <= application_columns
    assert {"resume_page_id", "bbox_json", "source_method", "verified_by", "verified_at"} <= evidence_columns
    assert {"extraction_method", "manual_text", "last_failure_at"} <= upload_columns

