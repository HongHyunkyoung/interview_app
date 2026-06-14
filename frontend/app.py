import streamlit as st
from utils import check_backend_health


st.set_page_config(
    page_title="AI 면접 코치",
    layout="wide",
)

def build_pages():
    """면접 코치 앱의 세 페이지를 등록하고 실행합니다."""
    
    with st.sidebar:
        st.divider()
        if check_backend_health():
            st.success("✅ FastAPI 연결 정상")
        else:
            st.error("❌ FastAPI 연결 확인 필요")
            st.caption("uvicorn 실행 여부와 8000번 포트를 확인하세요.")
    
    interview_page = st.Page(
        "pages/interview.py",
        title="면접 연습",
        icon="🎤",
    
    )
    resume_page = st.Page(
        "pages/resume.py",
        title="이력서 분석",
        icon="📄",
    )
    settings_page = st.Page(
        "pages/settings.py",
        title="설정",
        icon="⚙️",
    )
    history_page = st.Page(
        "pages/history.py",
        title="면접 기록",
        icon="📋",
    )
    pg = st.navigation(
        {
            "면접 코치": [interview_page, resume_page, history_page],
            "앱 설정": [settings_page],
        }
    )
    pg.run()


build_pages()

