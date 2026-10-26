# 관련 규정을 찾는다
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from src.database import save_policy_chunk, search_policy_chunks

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


    # st.write("조각 개수:",len(policy_messages))  
# for policy_message in policy_messages:
#     #st.write(policy_message)
#     print(policy_message)

def make_policy_chunks(policy_messages):
    chunks = []

    for policy_message in policy_messages:
        lines = policy_message.strip().splitlines()

        if not lines:
            continue

        section = lines[0]

        chunk = {
            "text": policy_message.strip(),
            "source": "policy.txt",
            "section": section
        }

        chunks.append(chunk)
    

    return chunks

def make_embedding(text):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=768
        )
    )

    return result.embeddings[0].values


RISK_KEYWORDS = {
    "식대한도 초과" : "식대",
    "택시비 사유 부족" : "택시비",
    "영수증누락" : "영수증",
    "중복 신청 의심" : "중복",
    "야근 교통비 한도초과" : "교통비",
    "사무용품 추가 승인" : "사무용품"
}


#PolicySearchAgent 
def find_policy_evidence(risk_type,policy_messages): # 함수를 사용할때 값을 받아오는 입력칸
    # risk_type과 policy_messages는 이 함수를 만들면서 처음 등장해도 돼.
    risk_word =RISK_KEYWORDS.get(risk_type)
    if risk_word is None:
        return "관련 규정 확인 필요"   # 검색할 단어가 없다 ->확인해라
        
    for policy_message in policy_messages:  #policy_messages 안에 들어 있는 여러 규정 문단을 하나씩 꺼내서 policy_message라는 이름으로 확인하겠다는 뜻이야.
        if risk_word in policy_message:
            return policy_message      # 찾았으면 그 문단
    # 돌려주고 끝
    return "관련 규정 확인 필요"   # for문 다 돌고도 못 찾음


# RISK_KEYWORDS.get(risk_type)--> ex)숙박비  =>RISK_KEYWORDS.get(risk_type)=None


REQUEST_MESSAGE = { # risk_type : 그 위험에 맞는 보완 요청
    "영수증누락": "해당 비용의 영수증을 첨부해 주세요.",
    "택시비 사유 부족": "택시 이용 사유를 작성해 주세요.",
    "중복 신청 의심": "중복 신청 여부를 확인해 주세요.",
    "식대한도 초과": "식대 한도 초과 사유를 확인해 주세요.",
    "사무용품 추가 승인": "사무용품 구매에 필요한 승인 내역을 확인해 주세요.",
    "야근 교통비 한도초과": "교통비 한도 초과 사유를 확인해 주세요."
}

def make_request_message(risk_type): 
   
    risk_request =REQUEST_MESSAGE.get(risk_type)
    if risk_request is None:
        return "요청사항을 작성하시오"   
    return risk_request



   

def find_similar_policies(risk_reason, top_k=3):
    query_embedding = make_embedding(risk_reason)

    results = search_policy_chunks(
        query_embedding,
        top_k
    )

    return results

def find_keyword_policies(query, policy_messages, top_k=3):
    matched_policies = []

    for keyword in RISK_KEYWORDS.values():
        if keyword in query:

            for policy_message in policy_messages:
                if keyword in policy_message:
                    matched_policies.append(policy_message)

    return matched_policies[:top_k]


    
if __name__ == "__main__":
    with open("policy.txt","r",encoding="utf-8")as f:  #열기
    #"r":읽고 | encoding="utf-8": 한글이 깨지지않게 | as f : 지금 열린 파일 이름을 잠깐 f라고 부를게

        policy_txt = f.read() #읽기
        policy_messages = policy_txt.split("\n\n") #자르기
    chunks = make_policy_chunks(policy_messages)
    

    for chunk in chunks:
        embedding = make_embedding(chunk["text"])

        saved_id = save_policy_chunk(
            chunk["text"],
            chunk["source"],
            embedding
        )

        print("저장 id:", saved_id)
        print("규정:", chunk["section"])
        print("-----")

    # 검색 테스트 (직접 실행할 때만 동작)
    risk_type = "식대한도 초과"
    risk_reason = "[식대 규정]\n일반 식대는 20,000원을 초과할 수 없다."

    keyword_result = find_policy_evidence(risk_type, policy_messages)
    vector_results = find_similar_policies(risk_reason, top_k=3)

    print("=== Keyword Search ===")
    print(keyword_result)

    print("=== Vector Search ===")
    for policy in vector_results:
        print(policy)





