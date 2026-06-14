# 이번 self에서 작성할 골격 파일입니다.
from __future__ import annotations

import streamlit as st
import httpx
from typing import Any

# 연결 위치 체크리스트
# ☐ AI 응답 생성 대기 중 표시할 위치 → interview.py의 handle_user_input
# ☐ 백엔드 연결 실패 공통 처리 → api_client.py의 try/except
# ☐ AI 응답 옆 피드백 위젯 → interview.py의 for message 루프
# ☐ 저장된 대화 키워드 검색 → interview.py의 사이드바
# ☐ roles.py, tools.py, agents.py 재작성 없이 import 유지

# ============================
# 2. 로딩·빈 상태 표시 함수
# ============================

def render_waiting_state(message:str) -> None:
    """면접 코치 응답 대기 상태를 화면에 표시다."""
    with st.spinner(message):
        pass

def render_empty_interview_state(message_count: int) -> None:
    """아직 면접이 시작되지 않았을 떄 첫 화면 안내를 표시한다."""
    placeholder = st.empty()
    if message_count == 0:
        placeholder.info("면접 답변을 입력하면 AI코치가 피드백을 드립니다.")

def render_streaming_answer(tokens) -> str:
    """수신 토큰을 하나의 placeholder에 누적 표시한다."""
    placeholder = st.empty()
    answer = ""

    for token in tokens:
        answer += token
        #커서 효과로 타이핑 중임을 표시
        placeholder.markdown(answer +"|")

    #완료 후 커서 제거
    placeholder.markdown(answer)
    return answer

# ============================
# 3. 에러 핸들링 유틸
# ============================

def format_error_message(error:Exception) -> dict[str, str]:
    """프론트엔드에서 보여 줄 오류 메시지와 표시 수준을 만든다."""
    if isinstance(error, httpx.ConnectError):
        return {
            "level": "error",
            "message": "백엔드 서버에 연결할 수 없습니다. 서버거 실행 중인지 확인해주세요."
        }
    elif isinstance(error, httpx.TimeoutException):
        return {
            "level": "warning",
            "message": "응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."
        }
    elif isinstance(error, httpx.HTTPStatusError):
        return {
            "level":"error",
            "message": f"서버 오류가 발생했습니다. (상태 코드: {error.response.status_code})"
        }
    else:
        return {
            "level":"error",
            "message": "알 수 없는 오류가 발생했습니다."
        }
    
def show_api_error(error: Exception) -> None:
    """오류 종류에 맞는 Streamlit 메시지를 표시한다."""
    result = format_error_message(error)
    if result["level"] == "warning":
        st.warning(result["message"])
    else:
        st.error(result["message"])

def check_backend_health(
        backend_url: str = "http://localhost:8000"
) -> bool:
    """fastAPI /health endpoint를 호출해 백엔드 생존 여부를 확인한다."""
    try:
        with httpx.Client(timeout=3.0) as client:
            response = client.get(f"{backend_url}/health")
            response.raise_for_status()
            return response.json().get("status") == "ok"
    except Exception:
        return False
    
# ============================
# 4. AI 응답별 피드백 위젯
# ============================

def render_feedback_widget(
        message_id:str,
        conversation_id: str,
        index: int,
) -> None:
    """AI 응답에 대한 thumbs 피드백 입력 위치를 만든다."""
    feedback_value = st.feedback(
        "thumbs",
        key=f"fb_{message_id}_{index}"
    )

    # None은 선택 전 상태 → is not None으로 검사 (0도 유효한 값)
    if feedback_value is not None:
        # 0=싫어요, 1=좋아요
        rating = "up" if feedback_value == 1 else "down"
        payload = {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "rating": rating,
        }
        safe_post_feedback(payload)

def safe_post_feedback(
        payload: dict[str, Any]
) -> dict[str, Any] | None:
    """피드백 저장 요청을 보내고 사용자 친화적인 오류 메시지를 표시한다."""
    try:
        response = httpx.post("http://localhost:8000/feedback",
                              json=payload,
                              timeout=5.0,
                              )
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError:
        st.error("피드백 저장 실패: 서버에 연결할 수 없습니다.")
    except Exception:
        st.error("피드백 저장 중 오류가 발생했습니다.")
        return None
    
 # ============================
# 5. 대화 검색·필터링 함수
# ============================

def filter_conversations(
        messages: list[dict[str, str]],
        keyword:str,
        roles:list[str],
) -> list[dict[str,str]]:
    """대화 내역에서 조건에 맞는 메시지를 찾는다."""
    #검색어 정규화
    normalized_keyword = keyword.strip().lower()
    filtered: list[dict[str, str]] = []

    for message in messages:
        # 1) keyword가 비어 있으면 내용 조건 항상 통과
        keyword_matches = (
            not normalized_keyword
            or normalized_keyword in message["content"].lower()
        )
        # 2) roles가 비어 있으면 역할 조건 항상 통과
        role_matches = (
            not roles
            or message['role'] in roles
        )

        if keyword_matches and role_matches:
            filtered.append(message)
    return filtered