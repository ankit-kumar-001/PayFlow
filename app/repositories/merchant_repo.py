from typing import List, Optional
from uuid import UUID
from app.db.pool import get_cursor

def create_merchant(user_id: str, business_name: str, api_key: str, api_secret_hash: str) -> dict:
    """
    Creates a new merchant in the database.
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO merchants (user_id, business_name, api_key, api_secret_hash, status)
            VALUES (%s, %s, %s, %s, 'active')
            RETURNING id, user_id, business_name, api_key, status, created_at
            """,
            (user_id, business_name, api_key, api_secret_hash)
        )
        row = cursor.fetchone()
        return {
            "id": row[0],
            "user_id": row[1],
            "business_name": row[2],
            "api_key": row[3],
            "status": row[4],
            "created_at": row[5]
        }

def get_merchant_by_id(merchant_id: str) -> Optional[dict]:
    """
    Retrieves a merchant by its ID.
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, user_id, business_name, api_key, api_secret_hash, status, created_at
            FROM merchants
            WHERE id = %s
            """,
            (merchant_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "user_id": row[1],
            "business_name": row[2],
            "api_key": row[3],
            "api_secret_hash": row[4],
            "status": row[5],
            "created_at": row[6]
        }

def get_merchant_by_api_key(api_key: str) -> Optional[dict]:
    """
    Retrieves a merchant by its API key.
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, user_id, business_name, api_key, api_secret_hash, status, created_at
            FROM merchants
            WHERE api_key = %s
            """,
            (api_key,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "user_id": row[1],
            "business_name": row[2],
            "api_key": row[3],
            "api_secret_hash": row[4],
            "status": row[5],
            "created_at": row[6]
        }

def get_merchants_by_user_id(user_id: str) -> List[dict]:
    """
    Retrieves all merchants owned by a user.
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, user_id, business_name, api_key, status, created_at
            FROM merchants
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,)
        )
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "user_id": row[1],
                "business_name": row[2],
                "api_key": row[3],
                "status": row[4],
                "created_at": row[5]
            }
            for row in rows
        ]
