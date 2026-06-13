import sys
import os
import streamlit as st
from api_client import render_streaming_answer

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from roles import ROLES, get_role, DEFAULT_ROLE_KEY


def get_interviewer_options() -> dict[str, str]:
    """면접관 유형의 키와 화면 표시 이름을 반환합니다."""
    return {role.key: role.name for role in ROLES.values()}

def get_system_prompt(role_key: str) -> str:
    """선택한 면접관 유형의 시스템 프롬프트를 반환합니다."""
    return get_role(role_key).system_prompt

def initialize_messages() -> None:
    """최초 1회만 초기 메시지를 세팅합니다."""
    if "messages" not in st.session_state:
        st.session_state.messages= [
            {
                "role":"assistant",
                "content": "안녕하세요! AI 면접 코치입니다. 면접 답변을 입력해 주세요."
            }
        ]

def handle_user_input(user_text: str) -> None:
    """사용자 입력을 받아 메시지 목록에 저장합니다."""
    # 사용자 메시지 저장
    st.session_state.messages.append({"role": "user", "content": user_text})

    # 말풍선 안에 placeholder 만들기
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = render_streaming_answer(
            placeholder=placeholder,
            question=user_text,
            answer=user_text,
            role=st.session_state.get("selected_role", "general"),
        )

    # 출력된 텍스트를 메시지 기록에 저장
    st.session_state.messages.append({"role": "assistant", "content": full_response})


# ============================
# 화면 구성
# ============================

with st.sidebar:
    st.header("면접관 설정")
    
    # selected_role 초기화 (최초 1회만)
    if "selected_role" not in st.session_state:
        st.session_state.selected_role = DEFAULT_ROLE_KEY
    
    # 면접관 유형 선택 위젯
    options = get_interviewer_options()
    
    selected = st.selectbox(
        "면접관 유형을 선택하세요",
        options=list(options.keys()),
        format_func=lambda x: options[x],
        index=list(options.keys()).index(st.session_state.selected_role)
    )    
    st.session_state.selected_role = selected
    
    st.divider()
    st.subheader("현재 설정")
    settings = st.session_state.get("settings", {})
    st.write("모델:", settings.get("model", "gpt-4o-mini"))
    st.write("역할:", settings.get("role_preset", "기술면접"))
    
# 메인화면
st.title("면접 연습")
st.caption("면접 연습을 도와드립니다. 답변을 입력해 주세요.")

initialize_messages()

with st.expander("면접 코치 설정 확인"):
    st.write("역할 프리셋 목록:", list(ROLES.keys()))
    st.write("현재 메시지 수:", len(st.session_state.messages))
    st.write("현재 선택된 면접관:", st.session_state.get("selected_role", DEFAULT_ROLE_KEY))
    current_role = st.session_state.get("selected_role", DEFAULT_ROLE_KEY)
    st.write("시스템 프롬프트 미리보기:")
    st.write(ROLES[current_role].system_prompt[:50] + "...")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

    
user_input = st.chat_input("면접 답변을 입력해 주세요.")
if user_input:
    handle_user_input(user_input)
    st.rerun()
    
# ============================
# day1-self2 TODO
# ============================
# TODO 1: 면접관 유형 사이드바 위젯 추가 (압박/편안/기술/인성 선택)
# TODO 2: 선택한 면접관 유형을 st.session_state에 저장하기
# TODO 3: st.write_stream 출력 흐름 연결 (임시 generator 사용)
# TODO 4: 면접 기록 (면접관 유형 + 질문 + 답변 + 코치 응답) 구조 설계
# ============================