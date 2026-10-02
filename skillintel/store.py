"""Tiny SQLite repository (thread-safe) for pseudonymised employee skill profiles."""

from __future__ import annotations

import json
import sqlite3
import threading


class ProfileStore:
    def __init__(self, path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._lock = threading.Lock()
        with self._lock:
            self._conn.execute(
                "CREATE TABLE IF NOT EXISTS employees ("
                "id TEXT PRIMARY KEY, skills TEXT NOT NULL)"
            )
            self._conn.commit()

    def upsert(self, employee_id: str, skills: set[str]) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO employees(id, skills) VALUES (?, ?) "
                "ON CONFLICT(id) DO UPDATE SET skills = excluded.skills",
                (employee_id, json.dumps(sorted(skills))),
            )
            self._conn.commit()

    def get(self, employee_id: str) -> set[str] | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT skills FROM employees WHERE id = ?", (employee_id,)
            ).fetchone()
        return set(json.loads(row[0])) if row else None

    def all(self) -> dict[str, set[str]]:
        with self._lock:
            rows = self._conn.execute("SELECT id, skills FROM employees").fetchall()
        return {emp: set(json.loads(skills)) for emp, skills in rows}

    def delete(self, employee_id: str) -> bool:
        with self._lock:
            cur = self._conn.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
            self._conn.commit()
        return cur.rowcount > 0
