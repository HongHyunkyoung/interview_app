"""---------------------
- 이 파일이 담당하는 것:
  → 이력서 .txt 업로드, 텍스트 읽기, 맞춤 질문 생성 요청 준비,
    Function Calling 확인 데이터 표시, 질문 생성 대시보드.

- 이 파일이 담당하지 않는 것:
  → 면접 채팅 전체 화면 복사, API 키 입력, 8주차 agents 파일 수정.

- Day 5 self1로 넘길 값:
  → resume_file_name, resume_questions, resume_question_count, resume_step4b_done.
"""

import streamlit as st
from docx import Document
import io


settings = st.session_state.get("settings", {})

st.title("이력서 분석")
st.caption(f"현재 질문 역할: {settings.get('role_preset', '기술 면접')}")

def read_resume_text(uploaded_file) -> str:
    """업로드된 이력서 파일에서 면접 질문 생성용 텍스트를 준비합니다."""
    #파일이 없으면 빈 문자열 반환
    if uploaded_file is None:
        return ""
    
    file_name = uploaded_file.name

    # .txt 파일 처리
    if file_name.endswith(".txt"):
        text = uploaded_file.read().decode("utf-8")

    # .docx 파일 처리
    elif file_name.endswith(".docx"):
        doc = Document(io.BytesIO(uploaded_file.read()))
        text = "\n".join([
            paragraph.text
            for paragraph in doc.paragraphs
            if paragraph.text.strip()
        ])
    else:
        st.warning("지원하지 않는 파일 형식입니다.")
        return ""

    if len(text.strip()) < 50:
        st.warning("이력서 내용이 너무 짧습니다. 최소 50자 이상 입력해주세요.")
        return ""

    return text

#파일 업로드 위젯
uploaded_file = st.file_uploader(
    "이력서 텍스트 파일을 업로드하세요",
    type=["txt", "docx"],
)

resume_text = read_resume_text(uploaded_file)

if resume_text:
    st.text_area(
        "이력서 미리보기 (앞 300자)",
        value=resume_text[:300] + "...",
        height=150,
        disabled=True,
    )
else:
    st.info(".txt 또는 .docx 형식의 이력서 파일을 업로드해주세요.")

def build_resume_question_request(
    resume_text:str,
    question_count: int,
) -> dict:
    """이력서 기반 면접 질문 생성 요청 값을 만듭니다."""
    settings = st.session_state.get("settings", {})

    return{
        "resume_text": resume_text,
        "question_count": question_count,
        "model": settings.get("model", "gpt-4o-mini"),
        "system_prompt":settings.get(
            "system_prompt",
            "당신은 전문 면접관입니다."
        ),
        "role_preset": settings.get("role_preset", "기술 면접"),
    }

# 질문 수 선택
question_count = st.number_input(
    "생성할 질문 수",
    min_value=3,
    max_value=10,
    value=5,
    step=1,
)

def render_function_call_result(result:dict) ->None:
    """질문 생성 결과와 도구 호출 확인 데이터를 분리해 표시합니다."""
    questions= result.get("questions", [])
    tool_calls = result.get("tool_calls", [])

    # 질문 목록 표시
    st.subheader("생성된 면접 질문")
    if questions:
        for i, q in enumerate(questions, 1):
            st.write(f"**{i}.** {q}")
    else:
        st.warning("생성된 질문이 없습니다.")

    # Function Calling 상세(접어두기)
    with st.expander("Function Calling 확인 데이터"):
        if tool_calls:
            st.json(tool_calls)
        else:
            st.write("호출 없음")

# 테스트용 샘플 결과
sample_result = {
    "questions": [
        "프로젝트에서 FastAPI를 사용한 이유를 설명해 주세요.",
        "SSE 응답이 끊겼을 때 어떤 순서로 확인하겠습니까?",
        "Streamlit과 FastAPI를 연결할 때 어떤 어려움이 있었나요?",
    ],
    "tool_calls": [
        {
            "name": "extract_resume_keywords",
            "arguments": {"section": "projects"},
            "result": {"keywords": ["FastAPI", "SSE", "Streamlit"]},
        }
    ],
}

def save_resume_question_state(
        file_name:str,
        questions: list[str],
) -> None:
    """이력서 기반 질문 생성 결과를 세션 상태에 저장합니다."""
    st.session_state.resume_file_name = file_name
    st.session_state.resume_questions = questions
    st.session_state.resume_question_count = len(questions)
    st.session_state.resume_step4b_done=len(questions) > 0

# 질문 생성 버튼
if st.button("이력서 기반 질문 생성", disabled=not resume_text):
    if not resume_text:
        st.error("이력서를 먼저 업로드해주세요.")
    else:
        request = build_resume_question_request(resume_text, question_count)

        # 임시 결과
        result = sample_result

        questions = result.get("questions", [])
        save_resume_question_state(uploaded_file.name, questions)
        render_function_call_result(result)
        st.success(f"{len(questions)}개 질문을 생성했습니다.")

def render_resume_dashboard()-> None:
    """이력서 기반 질문 생성 결과를 대시보드로 표시합니다."""
    questions = st.session_state.get("resume_questions", [])
    question_count = st.session_state.get("resume_question_count", 0)
    done = st.session_state.get("resume_step4b_done", False)
    file_name= st.session_state.get("resume_file_name", "없음")

    # 지표 표시
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("생성된 질문 수", question_count)
    with col2:
        st.metric("업로드 파일", file_name)

    with col3:
        st.metric("완료 상태", "완료" if done else "미완료")

    if questions:
        import pandas as pd

        def classify_length(q):
            if len(q) <= 30:
                return "단문 (30자 이하)"
            elif len(q) <= 60:
                return "중문 (32~60자)"
            else:
                return "장문 (60자 초과)"
        length_data = [classify_length(q) for q in questions]
        df = pd.DataFrame({"질문 길이": length_data})
        counts = df["질문 길이"].value_counts().reset_index()
        counts.columns = ["길이 분류", "개수"]
        st.bar_chart(counts.set_index("길이 분류"))

    # 진행률 표시( 목표 10문제 기준)
    progress = min(question_count/10, 1.0)
    st.progress(progress, text=f"목표 달성률: {int(progress * 100)}% (10문제 기준)")

st.divider()
render_resume_dashboard()

# ============================
# Day 5 self1 연결 메모
# ============================
# - frontend/utils.py에서 반복되는 상태/오류 표시 함수를 정리한다
# - report.py에서 resume_questions를 읽어 결과 리포트를 만든다
# - README.md에 실행 순서와 포트 정보를 정리한다
# ============================
