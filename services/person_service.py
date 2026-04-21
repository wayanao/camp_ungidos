from __future__ import annotations

from fastapi import HTTPException
from psycopg.errors import UniqueViolation

from config.database import get_connection
from schemas.person_schema import ChargeCreate, PaymentCreate, PersonCreate


def _serialize_person(row: dict) -> dict:
    return {
        "id": row["id"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "document": row["document"],
        "phone": row["phone"],
        "age": row["age"],
        "church": row["church"],
        "guardian_name": row["guardian_name"],
        "guardian_phone": row["guardian_phone"],
        "eps": row["eps"],
        "blood_type": row["blood_type"],
        "allergies": row["allergies"],
        "medications": row["medications"],
        "medical_conditions": row["medical_conditions"],
        "dietary_restrictions": row["dietary_restrictions"],
        "emergency_contact_name": row["emergency_contact_name"],
        "emergency_contact_phone": row["emergency_contact_phone"],
        "insurance_provider": row["insurance_provider"],
        "base_fee": row["base_fee"],
        "status": row["status"],
        "notes": row["notes"],
        "created_at": row["created_at"],
    }


def _serialize_charge(row: dict) -> dict:
    return {
        "id": row["id"],
        "person_id": row["person_id"],
        "concept": row["concept"],
        "amount": row["amount"],
        "due_date": row["due_date"],
        "notes": row["notes"],
        "created_at": row["created_at"],
    }


def _serialize_payment(row: dict) -> dict:
    return {
        "id": row["id"],
        "person_id": row["person_id"],
        "amount": row["amount"],
        "payment_date": row["payment_date"],
        "payment_method": row["payment_method"],
        "reference": row["reference"],
        "notes": row["notes"],
        "created_at": row["created_at"],
    }


def _row_to_balance(row: dict) -> dict:
    total_charged = round(float(row["total_charged"] or 0), 2)
    total_paid = round(float(row["total_paid"] or 0), 2)
    balance = round(total_charged - total_paid, 2)
    status = "al_dia" if balance <= 0 else "pendiente"

    return {
        "person_id": row["person_id"],
        "full_name": row["full_name"],
        "total_charged": total_charged,
        "total_paid": total_paid,
        "balance": balance,
        "status": status,
    }


def _fetch_people_balances(person_id: int | None = None) -> list[dict]:
    query = """
        SELECT
            p.id AS person_id,
            CONCAT(p.first_name, ' ', p.last_name) AS full_name,
            COALESCE(ch.total_charged, 0) AS total_charged,
            COALESCE(pa.total_paid, 0) AS total_paid
        FROM people p
        LEFT JOIN (
            SELECT person_id, SUM(amount) AS total_charged
            FROM charges
            GROUP BY person_id
        ) ch ON ch.person_id = p.id
        LEFT JOIN (
            SELECT person_id, SUM(amount) AS total_paid
            FROM payments
            GROUP BY person_id
        ) pa ON pa.person_id = p.id
    """
    params: tuple = ()

    if person_id is not None:
        query += " WHERE p.id = %s"
        params = (person_id,)

    query += " ORDER BY p.created_at DESC, p.id DESC"

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

    return [_row_to_balance(row) for row in rows]


def get_person_or_404(person_id: int) -> dict:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM people WHERE id = %s",
                (person_id,),
            )
            person = cursor.fetchone()
    if not person:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return person


def create_person(data: PersonCreate) -> dict:
    payload = data.model_dump()
    with get_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO people (
                        first_name, last_name, document, phone, age, church,
                        guardian_name, guardian_phone, eps, blood_type, allergies,
                        medications, medical_conditions, dietary_restrictions,
                        emergency_contact_name, emergency_contact_phone, insurance_provider,
                        base_fee, status, notes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (
                        payload["first_name"],
                        payload["last_name"],
                        payload["document"],
                        payload["phone"],
                        payload["age"],
                        payload["church"],
                        payload["guardian_name"],
                        payload["guardian_phone"],
                        payload["eps"],
                        payload["blood_type"],
                        payload["allergies"],
                        payload["medications"],
                        payload["medical_conditions"],
                        payload["dietary_restrictions"],
                        payload["emergency_contact_name"],
                        payload["emergency_contact_phone"],
                        payload["insurance_provider"],
                        payload["base_fee"],
                        payload["status"],
                        payload["notes"],
                    ),
                )
                person = cursor.fetchone()

                if payload["base_fee"] > 0:
                    cursor.execute(
                        """
                        INSERT INTO charges (person_id, concept, amount, due_date, notes)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            person["id"],
                            "Inscripcion campamento",
                            payload["base_fee"],
                            None,
                            "Cobro generado automaticamente al registrar la persona.",
                        ),
                    )
            connection.commit()
        except UniqueViolation as exc:
            connection.rollback()
            raise HTTPException(
                status_code=409,
                detail="Ya existe una persona con ese documento",
            ) from exc

    return _serialize_person(person)


def update_person(person_id: int, data: PersonCreate) -> dict:
    payload = data.model_dump()
    get_person_or_404(person_id)

    with get_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE people
                    SET
                        first_name = %s,
                        last_name = %s,
                        document = %s,
                        phone = %s,
                        age = %s,
                        church = %s,
                        guardian_name = %s,
                        guardian_phone = %s,
                        eps = %s,
                        blood_type = %s,
                        allergies = %s,
                        medications = %s,
                        medical_conditions = %s,
                        dietary_restrictions = %s,
                        emergency_contact_name = %s,
                        emergency_contact_phone = %s,
                        insurance_provider = %s,
                        base_fee = %s,
                        status = %s,
                        notes = %s
                    WHERE id = %s
                    RETURNING *
                    """,
                    (
                        payload["first_name"],
                        payload["last_name"],
                        payload["document"],
                        payload["phone"],
                        payload["age"],
                        payload["church"],
                        payload["guardian_name"],
                        payload["guardian_phone"],
                        payload["eps"],
                        payload["blood_type"],
                        payload["allergies"],
                        payload["medications"],
                        payload["medical_conditions"],
                        payload["dietary_restrictions"],
                        payload["emergency_contact_name"],
                        payload["emergency_contact_phone"],
                        payload["insurance_provider"],
                        payload["base_fee"],
                        payload["status"],
                        payload["notes"],
                        person_id,
                    ),
                )
                person = cursor.fetchone()
            connection.commit()
        except UniqueViolation as exc:
            connection.rollback()
            raise HTTPException(
                status_code=409,
                detail="Ya existe una persona con ese documento",
            ) from exc

    return _serialize_person(person)


def delete_person(person_id: int) -> None:
    get_person_or_404(person_id)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM people WHERE id = %s", (person_id,))
        connection.commit()


def list_people() -> list[dict]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM people ORDER BY created_at DESC, id DESC")
            rows = cursor.fetchall()
    return [_serialize_person(row) for row in rows]


def add_charge(person_id: int, data: ChargeCreate) -> dict:
    get_person_or_404(person_id)
    payload = data.model_dump()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO charges (person_id, concept, amount, due_date, notes)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    person_id,
                    payload["concept"],
                    payload["amount"],
                    payload["due_date"],
                    payload["notes"],
                ),
            )
            charge = cursor.fetchone()
        connection.commit()
    return _serialize_charge(charge)


def add_payment(person_id: int, data: PaymentCreate) -> dict:
    get_person_or_404(person_id)
    payload = data.model_dump()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO payments (
                    person_id, amount, payment_date, payment_method, reference, notes
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    person_id,
                    payload["amount"],
                    payload["payment_date"],
                    payload["payment_method"],
                    payload["reference"],
                    payload["notes"],
                ),
            )
            payment = cursor.fetchone()
        connection.commit()
    return _serialize_payment(payment)


def get_person_balance(person_id: int) -> dict:
    balances = _fetch_people_balances(person_id)
    if not balances:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return balances[0]


def get_person_detail(person_id: int) -> dict:
    person = get_person_or_404(person_id)
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM charges WHERE person_id = %s ORDER BY created_at DESC, id DESC",
                (person_id,),
            )
            charges = cursor.fetchall()
            cursor.execute(
                "SELECT * FROM payments WHERE person_id = %s ORDER BY payment_date DESC, id DESC",
                (person_id,),
            )
            payments = cursor.fetchall()

    return {
        "person": _serialize_person(person),
        "charges": [_serialize_charge(row) for row in charges],
        "payments": [_serialize_payment(row) for row in payments],
        "balance": get_person_balance(person_id),
    }


def list_debtors() -> list[dict]:
    return [balance for balance in _fetch_people_balances() if balance["balance"] > 0]


def list_all_payments() -> list[dict]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    pay.id, pay.person_id, pay.amount, pay.payment_date,
                    pay.payment_method, pay.reference, pay.notes, pay.created_at,
                    CONCAT(p.first_name, ' ', p.last_name) AS full_name,
                    p.document
                FROM payments pay
                JOIN people p ON p.id = pay.person_id
                ORDER BY pay.payment_date DESC, pay.id DESC
                """
            )
            rows = cursor.fetchall()
    return [
        {
            "id": r["id"],
            "person_id": r["person_id"],
            "full_name": r["full_name"],
            "document": r["document"],
            "amount": float(r["amount"]),
            "payment_date": r["payment_date"],
            "payment_method": r["payment_method"],
            "reference": r["reference"],
            "notes": r["notes"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]


def get_dashboard() -> dict:
    balances = _fetch_people_balances()
    total_charged = round(sum(item["total_charged"] for item in balances), 2)
    total_paid = round(sum(item["total_paid"] for item in balances), 2)
    total_pending = round(sum(item["balance"] for item in balances if item["balance"] > 0), 2)

    return {
        "total_people": len(balances),
        "total_charged": total_charged,
        "total_paid": total_paid,
        "total_pending": total_pending,
        "debtors": sum(1 for item in balances if item["balance"] > 0),
    }
