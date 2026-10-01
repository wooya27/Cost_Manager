from fastapi import FastAPI

# FastAPI 애플리케이션 객체
# 다른 프로그램이 AuditFlow 기능을 호출할 수 있는 "API 입구" 역할
app = FastAPI(
    title="AuditFlow AI API",
    description="비용정산 1차 검수 기능을 제공하는 API",
    version="0.1.0",
)


@app.get("/")
def root():
    """서버가 정상 실행 중인지 가장 간단히 확인하는 엔드포인트."""
    return {
        "service": "AuditFlow AI",
        "status": "running",
    }


@app.get("/health")
def health():
    """운영 환경에서 서버 생존 여부를 확인하기 위한 헬스 체크."""
    return {"status": "ok"}
