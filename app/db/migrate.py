import os
import logging
from app.db.pool import get_conn, release_conn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), 'migrations')

def run_migrations():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Create migrations table if missing
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    filename TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

            if not os.path.exists(MIGRATIONS_DIR):
                logger.info("Migrations directory does not exist.")
                return

            migration_files = sorted([f for f in os.listdir(MIGRATIONS_DIR) if f.endswith('.sql')])
            
            for filename in migration_files:
                cur.execute("SELECT 1 FROM schema_migrations WHERE filename = %s", (filename,))
                if not cur.fetchone():
                    logger.info(f"Applying migration: {filename}")
                    filepath = os.path.join(MIGRATIONS_DIR, filename)
                    with open(filepath, 'r') as f:
                        sql = f.read()
                    
                    try:
                        cur.execute(sql)
                        cur.execute("INSERT INTO schema_migrations (filename) VALUES (%s)", (filename,))
                        conn.commit()
                        logger.info(f"Successfully applied {filename}")
                    except Exception as e:
                        conn.rollback()
                        logger.error(f"Failed applying migration {filename}: {e}")
                        raise
                else:
                    logger.info(f"Skipping migration (already applied): {filename}")

    finally:
        release_conn(conn)

if __name__ == "__main__":
    logger.info("Starting database migrations...")
    run_migrations()
    logger.info("Migrations completed successfully.")
