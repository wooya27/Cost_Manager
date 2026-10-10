import os
import psycopg 
from dotenv import load_dotenv

load_dotenv()
#database 주소값 가져와
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg.connect(DATABASE_URL)# DATABASE_URL로 PostgreSQL 접속.” /문열고 들어가기

def create_tables(): # 표자체 만들기
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

    def save_audit_result(employee,
    department,
    category,
    amount,
    risk_type,
    risk_reason,
    policy_evidence,
    draft_message,
    draft_source
    ): # 장부에 실제 1결과 저장하기

     conn = get_connection() # DB실행

    with conn.cursor() as cur:
        cur.execute( # audit_results 표에 한 줄 추가
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
            RETURNING id; #
            """,# VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)   : 실제값 넣기
                #RETURNING id;: 방금 저장된 행 번호 알려줘
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

        new_id = cur.fetchone()[0] #→ 그 번호 꺼내기

        conn.commit() #→ 저장 확정
        conn.close()

        return new_id # → id를 FastAPI 쪽으로 돌려주기
