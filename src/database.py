import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

# database 주소값 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg.connect(DATABASE_URL)


def create_tables():
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute(
            """
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
            """
        )

    conn.commit()
    conn.close()


def save_audit_result(
    employee,
    department,
    category,
    amount,
    risk_type,
    risk_reason,
    policy_evidence,
    draft_message,
    draft_source
):
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO audit_results (
                employee,
                department,
                category,
                amount,
                risk_type,
                risk_reason,
                policy_evidence,
                draft_message,
                draft_source
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                employee,
                department,
                category,
                amount,
                risk_type,
                risk_reason,
                policy_evidence,
                draft_message,
                draft_source
            )
        )

        new_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return new_id

def get_audit_results():
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                id,
                employee,
                department,
                category,
                amount,
                risk_type,
                risk_reason,
                policy_evidence,
                draft_message,
                draft_source,
                review_status,
                created_at
            FROM audit_results
            ORDER BY id DESC;
            """
        )

        rows = cur.fetchall()

    conn.close()

    return rows
