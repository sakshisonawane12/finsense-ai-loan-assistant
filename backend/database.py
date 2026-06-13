"""
database.py — SQLite persistence layer
Lightweight, file-based, zero RAM overhead. Perfect for 8GB RAM laptops.
"""
import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

DB_PATH = "finsense.db"


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # safe concurrent writes
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT UNIQUE NOT NULL,
                hashed_pw   TEXT NOT NULL,
                created_at  TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS sessions (
                user_id     TEXT PRIMARY KEY,
                stage       TEXT DEFAULT 'start',
                amount      INTEGER,
                tenure      INTEGER,
                salary      INTEGER,
                aadhaar     TEXT,
                kyc_retries INTEGER DEFAULT 0,
                kyc_confidence INTEGER,
                max_eligible INTEGER,
                start_time  REAL,
                stage_start REAL,
                last_active REAL,
                updated_at  TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     TEXT NOT NULL,
                event       TEXT NOT NULL,
                detail      TEXT,
                status      TEXT DEFAULT 'INFO',
                confidence  INTEGER,
                rule        TEXT,
                explanation TEXT,
                ts          TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS applications (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     TEXT NOT NULL,
                ref_id      TEXT UNIQUE,
                amount      INTEGER,
                tenure      INTEGER,
                salary      INTEGER,
                decision    TEXT,
                emi         INTEGER,
                total_payable INTEGER,
                confidence  INTEGER,
                kyc_conf    INTEGER,
                credit_score INTEGER,
                risk_profile TEXT,
                pdf_path    TEXT,
                created_at  TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS dashboard_stats (
                id              INTEGER PRIMARY KEY CHECK (id = 1),
                total           INTEGER DEFAULT 0,
                approved        INTEGER DEFAULT 0,
                rejected        INTEGER DEFAULT 0,
                kyc_failures    INTEGER DEFAULT 0,
                escalations     INTEGER DEFAULT 0,
                sla_breaches    INTEGER DEFAULT 0,
                total_ms        INTEGER DEFAULT 0
            );

            INSERT OR IGNORE INTO dashboard_stats (id) VALUES (1);
        """)


# ── User ops ──────────────────────────────────────────────────────────────────
def create_user(username: str, hashed_pw: str) -> bool:
    try:
        with get_db() as db:
            db.execute("INSERT INTO users (username, hashed_pw) VALUES (?,?)",
                       (username.lower(), hashed_pw))
        return True
    except sqlite3.IntegrityError:
        return False


def get_user(username: str):
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE username=?",
                         (username.lower(),)).fetchone()
        return dict(row) if row else None


# ── Session ops ───────────────────────────────────────────────────────────────
def get_session(user_id: str) -> dict:
    with get_db() as db:
        row = db.execute("SELECT * FROM sessions WHERE user_id=?",
                         (user_id,)).fetchone()
        if row:
            return dict(row)
        # Create fresh session
        import time
        db.execute(
            "INSERT INTO sessions (user_id, last_active) VALUES (?,?)",
            (user_id, time.time())
        )
        return {"user_id": user_id, "stage": "start", "amount": None,
                "tenure": None, "salary": None, "aadhaar": None,
                "kyc_retries": 0, "kyc_confidence": None, "max_eligible": None,
                "start_time": None, "stage_start": None, "last_active": time.time()}


def update_session(user_id: str, **fields):
    import time
    fields["last_active"] = time.time()
    fields["updated_at"] = datetime.now().isoformat()
    cols = ", ".join(f"{k}=?" for k in fields)
    vals = list(fields.values()) + [user_id]
    with get_db() as db:
        db.execute(f"UPDATE sessions SET {cols} WHERE user_id=?", vals)


def reset_session(user_id: str):
    import time
    with get_db() as db:
        db.execute("""
            UPDATE sessions SET
                stage='start', amount=NULL, tenure=NULL, salary=NULL,
                aadhaar=NULL, kyc_retries=0, kyc_confidence=NULL,
                max_eligible=NULL, start_time=NULL, stage_start=NULL,
                last_active=?
            WHERE user_id=?
        """, (time.time(), user_id))


# ── Audit ops ─────────────────────────────────────────────────────────────────
def log_audit(user_id: str, event: str, detail: str,
              status="INFO", confidence=None, rule=None, explanation=None):
    with get_db() as db:
        db.execute("""
            INSERT INTO audit_logs
                (user_id, event, detail, status, confidence, rule, explanation)
            VALUES (?,?,?,?,?,?,?)
        """, (user_id, event, detail, status, confidence, rule, explanation))


def get_audit(user_id: str) -> list:
    with get_db() as db:
        rows = db.execute("""
            SELECT ts, event, detail, status, confidence, rule, explanation
            FROM audit_logs WHERE user_id=? ORDER BY id
        """, (user_id,)).fetchall()
        return [dict(r) for r in rows]


# ── Application ops ───────────────────────────────────────────────────────────
def save_application(user_id: str, **fields):
    cols = ", ".join(["user_id"] + list(fields.keys()))
    placeholders = ", ".join(["?"] * (len(fields) + 1))
    vals = [user_id] + list(fields.values())
    with get_db() as db:
        db.execute(f"INSERT INTO applications ({cols}) VALUES ({placeholders})", vals)


# ── Dashboard ops ─────────────────────────────────────────────────────────────
def increment_stat(field: str, amount: int = 1):
    with get_db() as db:
        db.execute(f"UPDATE dashboard_stats SET {field}={field}+? WHERE id=1",
                   (amount,))


def get_stats() -> dict:
    with get_db() as db:
        row = db.execute("SELECT * FROM dashboard_stats WHERE id=1").fetchone()
        return dict(row) if row else {}
