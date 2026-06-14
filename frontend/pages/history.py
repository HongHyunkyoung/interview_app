import uuid
from typing import TypedDict
import streamlit as st
from report import render_report_download


class InterviewMessage(TypedDict):
    role: str
    content: str

class InterviewSession(TypedDict):
    title: str
    messages: list[InterviewMessage]

def get_selected_conversation() -> InterviewSession | None:
    """리포트로 내보낼 현재 면접 세션을 반환한다."""
    conversations = st.session_state.get("conversations", {})
    current_id = st.session_state.get("current_session_id")
    if not current_id or current_id not in conversations:
        return None
    return conversations[current_id]

def ensure_session_state() -> None:
    """면접 세션 저장소와 현재 세션 ID를 초기화한다."""
    if "conversations" not in st.session_state:
        first_id = str(uuid.uuid4())
        st.session_state.conversations = {
            first_id: {
                "title": "면접 세션 1",
                "messages": []
            }
        }
        st.session_state.current_session_id = first_id

def add_new_session() -> None:
    """새 UUID 면접 세션을 추가하고 현재 세션으로 전환한다."""
    conversations = st.session_state.get("conversations", {})
    new_id = str(uuid.uuid4())
    session_number = len(conversations) + 1
    conversations[new_id] =  {
        "title": f"면접 세션 {session_number}",
        "messages": []
    }
    st.session_state.conversations = conversations
    st.session_state.current_session_id = new_id

def delete_current_session() -> None:
    """현재 세션을 삭제하고 남은 세션으로 안전하게 이동한다."""
    conversations = st.session_state.get("conversations", {})
    current_id = st.session_state.get("current_session_id")

    if not current_id or current_id not in conversations:
        return
    
    #마지막 세션은 삭제하지 않고 메시지만 비움
    if len(conversations) ==1:
        conversations[current_id]["messages"] = []
        return
    
    del conversations[current_id]
    st.session_state.current_session_id = next(iter(conversations))

# ============================
# 화면 구성
# ============================
ensure_session_state()

st.title("면접 기록")
st.caption("면접 세션을 관리하고 기록을 확인힙니다.")

conversations = st.session_state.get("conversations", {})
current_id = st.session_state.get("current_session_id")

#세션 목록 표시
st.subheader("세션 목록")
for sid, session in conversations.items():
    col1, col2 = st.columns([4, 1])
    with col1:
        if st.button(
            session["title"],
            key=f"select_{sid}",
            type="primary" if sid == current_id else "secondary"
        ):
            st.session_state.current_session_id = sid
            st.rerun()
    with col2:
        if st.button("🗑️", key=f"delete_{sid}"):
            st.session_state.current_session_id = sid
            delete_current_session()
            st.rerun()

if st.button("➕ 새 세션 추가"):
    add_new_session()
    st.rerun()

# 현재 세션 메시지 표시
st.divider()
current_session = get_selected_conversation()
if current_session:
    st.subheader(f"현재 세션: {current_session['title']}")
    messages =current_session.get("messages",[])
    if messages:
        for msg in messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
    else:
        st.info("이 세션에는 아직 대화가 없습니다.")

# 리포트 다운로드
st.divider()
st.subheader("리포트 내보내기")
render_report_download(
    session_id=current_id or "",
    conversation=current_session,
    usage_summary={
        "request_count":0,
        "total_tokens": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "daily_limit_ratio":0.0,
    }
)