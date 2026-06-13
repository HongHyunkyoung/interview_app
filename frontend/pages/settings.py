import streamlit as st

st.title("설정")
st.caption("면접 코치 앱 전체에서 공유할 설정을 관리합니다.")

DEFAULT_SETTINGS = {
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "system_prompt": "당신은 전문 면접관입니다. 지원자의 역량을 파악하는 심층 질문을 해주세요.",
    "role_preset": "기술 면접",
}

ROLE_PRESETS = {
    "기술 면접": "기술 역량을 중심으로 질문합니다.",
    "인성 면접": "협업과 태도를 중심으로 질문합니다.",
    "임원 면접": "비전과 조직 기여도를 중심으로 질문합니다.",
}


def ensure_setting() -> dict:
    """앱 전체에서 공유할 설정 dict를 준비합니다."""
    if "settings" not in st.session_state:
        st.session_state.settings = DEFAULT_SETTINGS.copy()
    return st.session_state.settings

settings = ensure_setting()

selected_model = st.selectbox(
    "모델 선택",
    options=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
    index=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"].index(
        settings.get("model", "gpt-4o-mini")
    ),
)

selected_temperature = st.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=settings.get("temperature",0.7),
    step=0.1
)

selected_role = st.selectbox(
    "역할 프리셋",
    options=list(ROLE_PRESETS.keys()),
    index=list(ROLE_PRESETS.keys()).index(
        settings.get("role_preset", "기술 면접")
    ),
)

selected_prompt = st.text_area(
    "시스템 프롬프트",
    value=settings.get("system_prompt", DEFAULT_SETTINGS["system_prompt"]),
    height=150,
)

if st.button("설정 저장"):
    st.session_state.settings ={
        "model": selected_model,
        "temperature": selected_temperature,
        "system_prompt": selected_prompt,
        "role_preset": selected_role,
    }
    st.success("설정을 저장했습니다.")