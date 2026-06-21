from app.db.pool import get_cursor

def create_user(email: str, password_hash: str, full_name: str = None) -> dict:
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO users (email, password_hash, full_name)
            VALUES (%s, %s, %s)
            RETURNING id, email, full_name, created_at
        """, (email, password_hash, full_name))
        row = cur.fetchone()
        if row:
            return {
                "id": row[0],
                "email": row[1],
                "full_name": row[2],
                "created_at": row[3]
            }
        return None

def get_user_by_email(email: str) -> dict:
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, email, password_hash, full_name, created_at
            FROM users
            WHERE email = %s
        """, (email,))
        row = cur.fetchone()
        if row:
            return {
                "id": row[0],
                "email": row[1],
                "password_hash": row[2],
                "full_name": row[3],
                "created_at": row[4]
            }
        return None

def get_user_by_id(user_id: str) -> dict:
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, email, password_hash, full_name, created_at
            FROM users
            WHERE id = %s
        """, (user_id,))
        row = cur.fetchone()
        if row:
            return {
                "id": row[0],
                "email": row[1],
                "password_hash": row[2],
                "full_name": row[3],
                "created_at": row[4]
            }
        return None
