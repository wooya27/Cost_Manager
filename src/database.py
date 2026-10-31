import os
import psycopg

from dotenv import load_dotenv
from psycopg.types.json import Jsonb
from pgvector import Vector
from pgvector.psycopg import register_vector


load_dotenv()

# DB 주소 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")


# =========================================================
# DB 연결
# =========================================================

def get_connection():
    return psycopg.connect(DATABASE_URL)


# =========================================================
# 테이블 생성
# =========================================================

def create_tables():
    conn = get_connection()

    with conn.cursor() as cur:

        # 테이블이 없으면 생성
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
                review_note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                risks JSONB DEFAULT '[]'::jsonb
            );
            """
        )

        # 기존 DB에 risks 컬럼이 없으면 추가
        cur.execute(
            """
            ALTER TABLE audit_results
            ADD COLUMN IF NOT EXISTS risks
            JSONB DEFAULT '[]'::jsonb;
            """
        )

        # Block 9 - 검수 메모
        cur.execute(
            """
            ALTER TABLE audit_results
            ADD COLUMN IF NOT EXISTS review_note TEXT;
            """
        )

        # Block 9 - 실제 검수 시간
        cur.execute(
            """
            ALTER TABLE audit_results
            ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP;
            """
        )

        # Block 9 - 마지막 수정 시간
        cur.execute(
            """
            ALTER TABLE audit_results
            ADD COLUMN IF NOT EXISTS updated_at
            TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            """
        )

    conn.commit()
    conn.close()


# =========================================================
# 감사 결과 저장
# =========================================================

def save_audit_result(
    employee,
    department,
    category,
    amount,
    risks,
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
                risks,
                risk_type,
                risk_reason,
                policy_evidence,
                draft_message,
                draft_source
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id;
            """,
            (
                employee,
                department,
                category,
                amount,
                Jsonb(risks or []),
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


# =========================================================
# 저장된 감사 결과 조회
# =========================================================

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
                risks,
                risk_type,
                risk_reason,
                policy_evidence,
                draft_message,
                draft_source,
                review_status,
                review_note,
                created_at,
                reviewed_at,
                updated_at
            FROM audit_results
            ORDER BY id DESC;
            """
        )

        rows = cur.fetchall()

    conn.close()

    return rows


# =========================================================
# Human Review 수정
# =========================================================

def update_review_status(
    audit_id,
    review_status,
    review_note=None
):
    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute(
            """
            UPDATE audit_results
            SET
                review_status = %s,
                review_note = %s,
                reviewed_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id;
            """,
            (
                review_status,
                review_note,
                audit_id
            )
        )

        row = cur.fetchone()

    conn.commit()
    conn.close()

    return row

def save_policy_chunk(text, source, embedding):
    conn = get_connection()

    register_vector(conn)

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id
            FROM policy_chunks
            WHERE text = %s AND source = %s
            """,
            (text, source)
        )

        existing = cur.fetchone()

        if existing:
            conn.close()
            return existing[0]

        cur.execute(
            """
            INSERT INTO policy_chunks (
                text,
                source,
                embedding
            )
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (
                text,
                source,
                Vector(embedding)
            )
        )

        new_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return new_id

def search_policy_chunks(query_embedding, top_k=3):
    conn = get_connection()

    register_vector(conn)

    query_vector = Vector(query_embedding)

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                id,
                text,
                source,
                1 - (embedding <=> %s) AS similarity
            FROM policy_chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (
                query_vector,
                query_vector,
                top_k
            )
        )

        results = cur.fetchall()

    conn.close()

    return results