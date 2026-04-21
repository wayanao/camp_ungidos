from __future__ import annotations

from fastapi import HTTPException

from config.database import get_connection
from schemas.expense_schema import ExpenseCreate


def _serialize(row: dict) -> dict:
    return {
        "id": row["id"],
        "concept": row["concept"],
        "amount": float(row["amount"]),
        "date": row["date"],
        "category": row["category"],
        "notes": row["notes"],
        "created_at": row["created_at"],
    }


def list_expenses() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM expenses ORDER BY date DESC, id DESC")
            rows = cur.fetchall()
    return [_serialize(r) for r in rows]


def create_expense(data: ExpenseCreate) -> dict:
    payload = data.model_dump()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO expenses (concept, amount, date, category, notes)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (payload["concept"], payload["amount"], payload["date"], payload["category"], payload["notes"]),
            )
            row = cur.fetchone()
        conn.commit()
    return _serialize(row)


def delete_expense(expense_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM expenses WHERE id = %s", (expense_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Egreso no encontrado")
            cur.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        conn.commit()
