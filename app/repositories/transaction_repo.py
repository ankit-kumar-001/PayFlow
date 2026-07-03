from typing import List, Optional
from app.db.pool import get_cursor

def _row_to_dict(row) -> Optional[dict]:
    if not row:
        return None
    return {
        "id": row[0],
        "payment_link_id": row[1],
        "merchant_id": row[2],
        "amount": row[3],
        "currency": row[4],
        "status": row[5],
        "payment_method": row[6],
        "created_at": row[7]
    }

def create_transaction(
    payment_link_id: Optional[str],
    merchant_id: str,
    amount: float,
    currency: str,
    status: str,
    payment_method: str
) -> dict:
    query = """
        INSERT INTO transactions (payment_link_id, merchant_id, amount, currency, status, payment_method)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, payment_link_id, merchant_id, amount, currency, status, payment_method, created_at
    """
    with get_cursor() as cursor:
        cursor.execute(query, (payment_link_id, merchant_id, amount, currency, status, payment_method))
        return _row_to_dict(cursor.fetchone())

def get_transaction_by_id(transaction_id: str) -> Optional[dict]:
    query = """
        SELECT id, payment_link_id, merchant_id, amount, currency, status, payment_method, created_at
        FROM transactions
        WHERE id = %s
    """
    with get_cursor() as cursor:
        cursor.execute(query, (transaction_id,))
        return _row_to_dict(cursor.fetchone())

def list_transactions_by_merchant(merchant_id: str, limit: int = 10, offset: int = 0) -> List[dict]:
    query = """
        SELECT id, payment_link_id, merchant_id, amount, currency, status, payment_method, created_at
        FROM transactions
        WHERE merchant_id = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    with get_cursor() as cursor:
        cursor.execute(query, (merchant_id, limit, offset))
        return [_row_to_dict(row) for row in cursor.fetchall()]

def list_transactions_by_link(payment_link_id: str, limit: int = 10, offset: int = 0) -> List[dict]:
    query = """
        SELECT id, payment_link_id, merchant_id, amount, currency, status, payment_method, created_at
        FROM transactions
        WHERE payment_link_id = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    with get_cursor() as cursor:
        cursor.execute(query, (payment_link_id, limit, offset))
        return [_row_to_dict(row) for row in cursor.fetchall()]
