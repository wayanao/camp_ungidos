from __future__ import annotations

import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


def load_env_file() -> None:
    if not ENV_PATH.exists():
        return

    for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip()


def get_database_url() -> str:
    load_env_file()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL no esta configurada. Agrega la cadena de conexion de Supabase en .env."
        )
    return database_url


def get_connection():
    return psycopg.connect(get_database_url(), row_factory=dict_row)


def init_db() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id BIGSERIAL PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS people (
                    id BIGSERIAL PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    document TEXT NOT NULL UNIQUE,
                    phone TEXT,
                    age INTEGER,
                    church TEXT,
                    guardian_name TEXT,
                    guardian_phone TEXT,
                    eps TEXT,
                    blood_type TEXT,
                    allergies TEXT,
                    medications TEXT,
                    medical_conditions TEXT,
                    dietary_restrictions TEXT,
                    emergency_contact_name TEXT,
                    emergency_contact_phone TEXT,
                    insurance_provider TEXT,
                    base_fee NUMERIC(12, 2) NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'registrado',
                    notes TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
            cursor.execute("ALTER TABLE people ADD COLUMN IF NOT EXISTS eps TEXT;")
            cursor.execute("ALTER TABLE people ADD COLUMN IF NOT EXISTS blood_type TEXT;")
            cursor.execute("ALTER TABLE people ADD COLUMN IF NOT EXISTS allergies TEXT;")
            cursor.execute("ALTER TABLE people ADD COLUMN IF NOT EXISTS medications TEXT;")
            cursor.execute("ALTER TABLE people ADD COLUMN IF NOT EXISTS medical_conditions TEXT;")
            cursor.execute("ALTER TABLE people ADD COLUMN IF NOT EXISTS dietary_restrictions TEXT;")
            cursor.execute("ALTER TABLE people ADD COLUMN IF NOT EXISTS emergency_contact_name TEXT;")
            cursor.execute("ALTER TABLE people ADD COLUMN IF NOT EXISTS emergency_contact_phone TEXT;")
            cursor.execute("ALTER TABLE people ADD COLUMN IF NOT EXISTS insurance_provider TEXT;")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS charges (
                    id BIGSERIAL PRIMARY KEY,
                    person_id BIGINT NOT NULL REFERENCES people (id) ON DELETE CASCADE,
                    concept TEXT NOT NULL,
                    amount NUMERIC(12, 2) NOT NULL,
                    due_date DATE,
                    notes TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS payments (
                    id BIGSERIAL PRIMARY KEY,
                    person_id BIGINT NOT NULL REFERENCES people (id) ON DELETE CASCADE,
                    amount NUMERIC(12, 2) NOT NULL,
                    payment_date DATE NOT NULL,
                    payment_method TEXT NOT NULL,
                    reference TEXT,
                    notes TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id BIGSERIAL PRIMARY KEY,
                    concept TEXT NOT NULL,
                    amount NUMERIC(12, 2) NOT NULL,
                    date DATE NOT NULL,
                    category TEXT NOT NULL DEFAULT 'general',
                    notes TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
            seed_defaults(cursor)
        connection.commit()


def seed_defaults(cursor) -> None:
    cursor.execute(
        """
        INSERT INTO users (email, password, role)
        VALUES (%s, %s, %s)
        ON CONFLICT (email) DO NOTHING
        """,
        ("admin@test.com", "1234", "admin"),
    )
