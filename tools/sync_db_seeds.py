import os
import sys
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

load_dotenv(os.path.join(base_dir, ".env"))

from api.db_adapter import DatabaseAdapter
from api.user_store import UserStore

def sync_seeds():
    if not DatabaseAdapter.is_postgres_configured():
        print("[DB] PostgreSQL not configured.")
        return

    DatabaseAdapter.init_schema()
    seeds = UserStore._get_seed_users()
    for u in seeds.values():
        DatabaseAdapter.save_user(u)
        print(f"[DB] Saved {u['email']} to PostgreSQL")

    conn = DatabaseAdapter._get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM penta_users WHERE email LIKE '%@pentactopus.com'")
            print("[DB] Cleaned up legacy @pentactopus.com users")
        conn.close()

if __name__ == "__main__":
    sync_seeds()
