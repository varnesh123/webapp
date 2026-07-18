"""
models.py
Database layer using Python's built-in sqlite3 module - a real relational
database (proper schema, types, and a unique index on title) with zero
extra dependencies to install.

DB_PATH is read from an environment variable so the same code runs
locally and on a host with a persistent disk without any changes.
"""

import os
import sqlite3
from contextlib import contextmanager


def resolve_db_path() -> str:
    raw_path = os.environ.get("DB_PATH") or os.environ.get("DATABASE_URL") or ""

    if raw_path.startswith("sqlite:///"):
        raw_path = raw_path[len("sqlite:///"):]

    if raw_path.startswith("sqlite://"):
        raw_path = raw_path[len("sqlite://"):]

    if raw_path and "://" in raw_path:
        raise ValueError("This app only supports SQLite databases for deployment.")

    if not raw_path:
        raw_path = os.path.join(os.path.dirname(__file__), "movies.db")

    if not os.path.isabs(raw_path):
        raw_path = os.path.abspath(os.path.join(os.path.dirname(__file__), raw_path))

    db_dir = os.path.dirname(raw_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    return raw_path


DB_PATH = resolve_db_path()

SCHEMA = """
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    rating_sum REAL NOT NULL DEFAULT 0,
    votes INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


# ---------- shaping rows for the templates/API ----------

def _row_to_dict(row: sqlite3.Row) -> dict:
    votes = row["votes"]
    avg = round(row["rating_sum"] / votes, 2) if votes else 0
    return {
        "title": row["title"],
        "display_title": row["title"].title(),
        "avg_rating": avg,
        "votes": votes,
    }


# ---------- query helpers used by the routes ----------

def add_rating(title: str, rating: float) -> str:
    """Add a vote for `title`. Returns 'updated' or 'created'."""
    title = title.strip().lower()
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM movies WHERE title = ?", (title,)
        ).fetchone()

        if existing:
            conn.execute(
                "UPDATE movies SET rating_sum = rating_sum + ?, votes = votes + 1 "
                "WHERE title = ?",
                (rating, title),
            )
            return "updated"
        else:
            conn.execute(
                "INSERT INTO movies (title, rating_sum, votes) VALUES (?, ?, 1)",
                (title, rating),
            )
            return "created"


def delete_movie(title: str) -> bool:
    title = title.strip().lower()
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM movies WHERE title = ?", (title,))
        return cur.rowcount > 0


def all_movies(query: str = "", sort_by: str = "title") -> list:
    sql = "SELECT title, rating_sum, votes FROM movies"
    params = ()
    if query:
        sql += " WHERE title LIKE ?"
        params = (f"%{query.strip().lower()}%",)

    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()

    movies = [_row_to_dict(r) for r in rows]

    if sort_by == "rating":
        movies.sort(key=lambda m: m["avg_rating"], reverse=True)
    elif sort_by == "votes":
        movies.sort(key=lambda m: m["votes"], reverse=True)
    else:
        movies.sort(key=lambda m: m["title"])

    return movies


def stats() -> dict:
    with get_conn() as conn:
        rows = conn.execute("SELECT title, rating_sum, votes FROM movies").fetchall()

    if not rows:
        return {"count": 0, "avg_of_all": 0, "most_voted": None}

    movies = [_row_to_dict(r) for r in rows]
    avgs = [m["avg_rating"] for m in movies]
    most_voted = max(movies, key=lambda m: m["votes"])
    return {
        "count": len(movies),
        "avg_of_all": round(sum(avgs) / len(avgs), 2),
        "most_voted": most_voted["display_title"],
    }
