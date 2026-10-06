import os
import psycopg 
from dotenv import load_dotenv

load_dotenv()
#database 주소값 가져와
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg.connect(DATABASE_URL)# DATABASE_URL로 PostgreSQL 접속.” /문열고 들어가기

def create_tables():
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_results (
                id SERIAL PRIMARY KEY,
                employee TEXT NOT NULL,
                department TEXT,
                category TEXT,
                amount INTEGER,
                risk_type TEXT,
                risk_reason TEXT,
                policy_evidence TEXT,
                draft_message TEXT,
                draft_source TEXT,
                review_status TEXT DEFAULT 'unreviewed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

    conn.commit()
    conn.close()