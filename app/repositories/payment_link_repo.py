from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.db.pool import get_cursor

def _row_to_dict(row) -> Optional[dict]:
    if not row:
        return None
    return {
        "id": row[0],
        "merchant_id": row[1],
        "amount": row[2],
        "currency": row[3],
        "description": row[4],
        "status": row[5],
        "expires_at": row[6],
        "created_at": row[7]
    }

def create_payment_link(merchant_id: str, amount: float, currency: str, description: Optional[str], expires_at: Optional[datetime], status: str = "created") -> dict:
    query = """
        INSERT INTO payment_links (merchant_id, amount, currency, description, status, expires_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, merchant_id, amount, currency, description, status, expires_at, created_at
    """
    with get_cursor() as cursor:
        cursor.execute(query, (merchant_id, amount, currency, description, status, expires_at))
        return _row_to_dict(cursor.fetchone())

def get_payment_link_by_id(link_id: str) -> Optional[dict]:
    query = """
        SELECT id, merchant_id, amount, currency, description, status, expires_at, created_at
        FROM payment_links
        WHERE id = %s
    """
    with get_cursor() as cursor:
        cursor.execute(query, (link_id,))
        return _row_to_dict(cursor.fetchone())

def list_payment_links_by_merchant(merchant_id: str, limit: int = 10, offset: int = 0) -> List[dict]:
    query = """
        SELECT id, merchant_id, amount, currency, description, status, expires_at, created_at
        FROM payment_links
        WHERE merchant_id = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    with get_cursor() as cursor:
        cursor.execute(query, (merchant_id, limit, offset))
        return [_row_to_dict(row) for row in cursor.fetchall()]

def update_payment_link_status(link_id: str, status: str) -> Optional[dict]:
    query = """
        UPDATE payment_links
        SET status = %s
        WHERE id = %s
        RETURNING id, merchant_id, amount, currency, description, status, expires_at, created_at
    """
    with get_cursor() as cursor:
        cursor.execute(query, (status, link_id))
        return _row_to_dict(cursor.fetchone())
