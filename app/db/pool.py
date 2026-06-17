import logging
from contextlib import contextmanager
from psycopg2.pool import ThreadedConnectionPool
import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize connection pool
try:
    pg_pool = ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        host=settings.PG_HOST,
        port=settings.PG_PORT,
        user=settings.PG_USER,
        password=settings.PG_PASSWORD,
        dbname=settings.PG_DB
    )
except Exception as e:
    logger.error(f"Failed to initialize database connection pool: {e}")
    pg_pool = None

# Initialize Redis client
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )
except Exception as e:
    logger.error(f"Failed to initialize Redis client: {e}")
    redis_client = None

def get_conn():
    if not pg_pool:
        raise Exception("Database pool is not initialized.")
    return pg_pool.getconn()

def release_conn(conn):
    if pg_pool and conn:
        pg_pool.putconn(conn)

@contextmanager
def get_cursor():
    conn = get_conn()
    cursor = None
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        release_conn(conn)
