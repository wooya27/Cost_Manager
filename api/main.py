
from fastapi import FastAPI # FastAPI라는 도구를 갖고온다
from pydantic import BaseModel #들어오는ㄴ 데이터의 규격을 정의하고 검사하기 위한 BaseModel을 갖고온다
app = FastAPI() # app이라는 변수에 FastAPI 서버하나를 만든다

# AuditFlow가 받을 비용 데이터의 양식을 만든다.
class ExpenseRequest(BaseModel): # 컬럼양식
    employee: str
    department: str
    category: str
    amount: int
    date: str
    vendor: str
    reason: str | None = None # reason은 글자일 수도 있고, 비어 있을 수도 있다.
    has_receipt: str

# 누군가 서버의 / 주소를 조회하면 root()를 실행해서 "running"이라는 결과를 돌려준다
@app.get("/")
def root():
    return{"status": "running"}



@app.post("/audit") # 누군가 /audit 주소로 POST 요청을 보내면 아래 함수를 실행해라.
                    # 들어온 비용 데이터를 expense라는 이름으로 받아라.+ 단, 데이터 형식은 ExpenseRequest 규칙을 따라야 한다.
                    #expense라는 데이터를 받을 건데, ExpenseRequest 형식이어야 해.
def audit_expense(expense: ExpenseRequest): # 현재함수는 아무처리도 아직안함. 입력->받고=확인->다시 보냄


          # 1. 비용 데이터를 DataFrame으로 바꾸고

            # 2. 위험 탐지하고

            # 3. 규정 찾고

            # 4. 초안 만들고

            # 5. 결과를 돌려준다



    return {
        "message": "비용 데이터를 정상적으로 받았습니다.",
        "expense": expense
    }



