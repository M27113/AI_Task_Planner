import sqlite3
from datetime import datetime
from typing import Optional
from pathlib import Path

DB_PATH = Path("plans.db")

def clean_plan_output(plan):
    """Remove empty lines or lines containing only 'None' from the plan text."""
    if not plan:
        return ""
    if isinstance(plan, list):
        plan = "\n".join(str(p) for p in plan)
    return "\n".join(line for line in plan.splitlines() if line.strip() and line.strip().lower() != "none")


def init_db():
    """Initialize the database and create the table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS plans (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               goal TEXT NOT NULL,
               plan_text TEXT NOT NULL,
               metadata TEXT,
               created_at TEXT NOT NULL
           )"""
    )
    conn.commit()
    conn.close()

def save_plan(goal: str, plan_text: str, metadata: Optional[str] = None) -> int:
    """Save a new plan and return its ID."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    created_at = datetime.utcnow().isoformat()

    # Clean plan_text before saving
    plan_text = clean_plan_output(plan_text)

    c.execute(
        "INSERT INTO plans (goal, plan_text, metadata, created_at) VALUES (?, ?, ?, ?)",
        (goal, plan_text, metadata or "", created_at),
    )
    plan_id = c.lastrowid
    conn.commit()
    conn.close()
    return plan_id

def fetch_plans():
    """Fetch all saved plans with cleaning applied."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, goal, plan_text, created_at FROM plans ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    # Apply cleaning before returning
    cleaned_rows = []
    for pid, goal, plan_text, created_at in rows:
        plan_text = clean_plan_output(plan_text)
        cleaned_rows.append((pid, goal, plan_text, created_at))
    return cleaned_rows
