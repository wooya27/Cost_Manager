from src.policy_retriever import find_policy_evidence, policy_messages
from src.draft_generator import make_draft
from src.observability import log_workflow

# state = 현재 작업정보를 들고다니는 가방
# node = workflow 에서 자기 한가지 일만 하는 함수 
# node 함수 3개 만든것
    # 위험 확인 담당자 만들기 
    # 규정 검색 담당자 만들기 
    # 초안 작성 담당자 만들기 
    
# 1. 위험 확인 Node
    # 정확히 말하면 아무것도 안 하는 게 아니라, 받은 state를 그대로 다음 단계로 넘기는 통과(pass-through) Node야.
    # 위험 정보가 이미 들어왔는지 확인하는 자리인데, 지금은 앞 단계에서 risk_type, risk_reason이 이미 만들어져 있으니까 그대로 넘긴다.”
def check_risk_node(state):
    return state

# 2. 규정 확인 Node
def policy_search_node(state): #현재 작업 정보를 state로 받아서 규정 검색을 담당하는 작업 단계를 만든다.
    risk_type = state["risk_type"]

    evidence = find_policy_evidence( 
        risk_type,
        policy_messages
    )

    state["policy_evidence"] = evidence #찾은 규정 근거를 State의 policy_evidence 칸에 써 넣는다.
    
    return state

# 3. 초안 생성 Node
def draft_message_node(state):  #초안생성을 node가 일했으니까, 일한결과를 state에도 기록해줘야 다음단계를 쓸수있다
    message, source = make_draft(state)
    # state가 함수 안으로 들어가는 순간, 함수 내부에서는 그걸 row라는 이름으로 부르게 돼.
    # state라는 표/가방 안에 "draft_message"라는 칸을 만들고, 오른쪽 message 안에 들어 있는 값을 그 칸에 넣어라.
    # 오른쪽 message 안에 들어 있는 값을 그 칸에 넣어라.

    state["draft_message"] = message # node 안에 잠깐 존재하는 임시변수
    state["draft_source"] = source

    return state

# state를 위험 확인 Node에 넣고 
# 그 결과 state를 규정 검색 Node에 넣고 
# 그 결과를 다시 초안 생성 Node에 넣는다.
def run_workflow(state): # node들을 연결하는 함수
    state = check_risk_node(state)
    state = policy_search_node(state)
    state = draft_message_node(state)

    log_workflow(state) #현재 결과를 파일에 기록
    return state


if __name__ == "__main__":

    test_state = {
        "employee": "김민수",
        "amount": 50000,
        "category": "식대",
        "risk_type": "영수증누락",
        "risk_reason": "영수증 없음"
    }

    result = run_workflow(test_state)

    print("규정 근거:", result["policy_evidence"])
    print("보완 요청 초안:", result["draft_message"])
    print("초안 출처:", result["draft_source"])