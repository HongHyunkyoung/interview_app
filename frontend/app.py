import streamlit as st


st.set_page_config(
    page_title="AI 면접 코치",
    layout="wide",
)

def build_pages():
    """면접 코치 앱의 세 페이지를 등록하고 실행합니다."""
    interview_page = st.Page(
        "pages/interview.py",
        title="면접 연습",
    )
    resume_page = st.Page(
        "pages/resume.py",
        title="이력서 분석",
    )
    settings_page = st.Page(
        "pages/settings.py",
        title="설정",
    )
    pg = st.navigation(
        {
            "면접 코치": [interview_page, resume_page],
            "앱 설정": [settings_page],
        }
    )
    pg.run()


build_pages()

