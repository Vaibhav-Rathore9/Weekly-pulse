"""
SQLite state store for idempotency and run tracking.

Table: runs
  - product       TEXT
  - iso_week      TEXT      (e.g. "2026-W17")
  - status        TEXT      (pending | dry_run | delivered | partial | failed)
  - started_at    TEXT      (ISO-8601)
  - completed_at  TEXT      (ISO-8601, nullable)
  - doc_heading   TEXT      (nullable — filled after Docs delivery)
  - message_id    TEXT      (nullable — filled after Gmail delivery)
  - review_count  INTEGER   (nullable)
  - theme_count   INTEGER   (nullable)

Primary key: (product, iso_week)
"""

import os
import sqlite3
from datetime import datetime, timezone


_DEFAULT_DB_PATH = os.path.join("data", "pulse_state.db")


def _db_path() -> str:
    return os.environ.get("PULSE_DB_PATH", _DEFAULT_DB_PATH)


def _get_connection() -> sqlite3.Connection:
    """Return a connection, creating the DB and table if needed."""
    path = _db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            product      TEXT    NOT NULL,
            iso_week     TEXT    NOT NULL,
            status       TEXT    NOT NULL DEFAULT 'pending',
            started_at   TEXT    NOT NULL,
            completed_at TEXT,
            doc_heading  TEXT,
            message_id   TEXT,
            review_count INTEGER,
            theme_count  INTEGER,
            PRIMARY KEY (product, iso_week)
        );
    """)
    conn.commit()
    return conn


def is_already_delivered(product: str, iso_week: str) -> bool:
    """Check if a run has already been successfully delivered."""
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT status FROM runs WHERE product = ? AND iso_week = ?",
            (product, iso_week),
        ).fetchone()
        return row is not None and row[0] == "delivered"
    finally:
        conn.close()


def is_dry_run_recorded(product: str, iso_week: str) -> bool:
    """Check if a dry-run has been recorded (does NOT block real runs)."""
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT status FROM runs WHERE product = ? AND iso_week = ?",
            (product, iso_week),
        ).fetchone()
        return row is not None and row[0] == "dry_run"
    finally:
        conn.close()


def record_run(
    product: str,
    iso_week: str,
    status: str,
    review_count: int | None = None,
    theme_count: int | None = None,
    doc_heading: str | None = None,
    message_id: str | None = None,
) -> None:
    """Insert or update a run record."""
    now = datetime.now(timezone.utc).isoformat()
    conn = _get_connection()
    try:
        conn.execute(
            """
            INSERT INTO runs (product, iso_week, status, started_at, completed_at,
                              doc_heading, message_id, review_count, theme_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(product, iso_week) DO UPDATE SET
                status       = excluded.status,
                completed_at = excluded.completed_at,
                doc_heading  = COALESCE(excluded.doc_heading, runs.doc_heading),
                message_id   = COALESCE(excluded.message_id, runs.message_id),
                review_count = COALESCE(excluded.review_count, runs.review_count),
                theme_count  = COALESCE(excluded.theme_count, runs.theme_count)
            """,
            (product, iso_week, status, now, now,
             doc_heading, message_id, review_count, theme_count),
        )
        conn.commit()
    finally:
        conn.close()


def get_run(product: str, iso_week: str) -> dict | None:
    """Fetch a run record as a dictionary, or None if not found."""
    conn = _get_connection()
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM runs WHERE product = ? AND iso_week = ?",
            (product, iso_week),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
