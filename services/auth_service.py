from config.database import get_connection


def authenticate_user(email: str, password: str):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, email, password, role
                FROM users
                WHERE email = %s AND password = %s
                """,
                (email, password),
            )
            return cursor.fetchone()
