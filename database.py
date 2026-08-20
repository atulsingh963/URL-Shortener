import os
import sqlite3
from pathlib import Path

# Path configuration
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "shortly.db"


def get_db_connection():
    """Returns a SQLite connection with row_factory set to sqlite3.Row."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database schema if it doesn't already exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_code TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                click_count INTEGER DEFAULT 0
            )
            """
        )
        conn.commit()


def code_exists(short_code):
    """Checks if a short code already exists in the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM urls WHERE short_code = ? LIMIT 1", (short_code,)
        )
        return cursor.fetchone() is not None


def create_url(original_url, short_code):
    """Inserts a new short URL record into the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
            (original_url, short_code),
        )
        conn.commit()
        return {
            "id": cursor.lastrowid,
            "original_url": original_url,
            "short_code": short_code,
            "click_count": 0,
        }


def get_url_and_increment_clicks(short_code):
    """
    Retrieves the original URL for a short code and increments its click count atomically.
    Returns dictionary with url details if found, or None if not found.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM urls WHERE short_code = ?", (short_code,)
        )
        row = cursor.fetchone()
        if not row:
            return None

        cursor.execute(
            "UPDATE urls SET click_count = click_count + 1 WHERE short_code = ?",
            (short_code,),
        )
        conn.commit()

        return dict(row)


def get_stats(short_code):
    """
    Retrieves statistical details for a short code without incrementing click count.
    Returns dictionary with url details if found, or None if not found.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, original_url, short_code, created_at, click_count FROM urls WHERE short_code = ?",
            (short_code,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return dict(row)
