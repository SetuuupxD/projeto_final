import sqlite3
from pathlib import Path
import os
import hashlib
import shutil

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "database.db")


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """Gera ou utiliza salt e retorna (salt, digest)."""
    if salt is None:
        salt = os.urandom(16).hex()
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return salt, digest


def db_connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Cria/atualiza banco e adiciona usuários padrão se não existirem."""
    Path(BASE_DIR).mkdir(parents=True, exist_ok=True)

    # backup se já existir
    if os.path.exists(DB_PATH):
        backup_path = DB_PATH + ".backup"
        try:
            shutil.copy2(DB_PATH, backup_path)
        except Exception:
            pass

    conn = db_connect()
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            professor TEXT,
            turma TEXT,
            payment_date TEXT,
            payment_method TEXT,
            assinatura TEXT,
            status_pagamento TEXT DEFAULT 'Pendente'
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            month TEXT,
            year INTEGER,
            payment_date TEXT,
            payment_method TEXT,
            amount REAL,
            status_pagamento TEXT DEFAULT 'Pendente',
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()

    # cria usuários padrão
    def ensure_user(username: str, password: str, is_admin: bool):
        cur.execute("SELECT id FROM users WHERE username=?", (username,))
        if cur.fetchone() is None:
            salt, digest = hash_password(password)
            cur.execute("INSERT INTO users (username, salt, password_hash, is_admin) VALUES (?,?,?,?)",
                        (username, salt, digest, 1 if is_admin else 0))

    ensure_user("admin", "admin", True)
    ensure_user("user", "123", False)

    conn.commit()
    conn.close()


def verify_user(username: str, password: str) -> tuple[bool, bool]:
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT salt, password_hash, is_admin FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False, False
    salt, stored_hash, is_admin = row
    _, digest = hash_password(password, salt)
    return (digest == stored_hash, bool(is_admin == 1))