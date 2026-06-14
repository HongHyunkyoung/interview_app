import streamlit as st
import pandas as pd


def render_final_dashboard(usage_summary: dict) -> None:
    """최종 제출 전 사용량과 진행 상태를 대시보드로 표시한다."""

    st.subheader("📊 사용량 대시보드")

    # 지표 표시
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "총 요청 수",
            f"{usage_summary.get('request_count', 0)}회"
        )
    with col2:
        st.metric(
            "총 토큰",
            f"{usage_summary.get('total_tokens', 0):,}"
        )

    # 토큰 비율 차트
    prompt_tokens = usage_summary.get("prompt_tokens", 0)
    completion_tokens = usage_summary.get("completion_tokens", 0)

    if prompt_tokens or completion_tokens:
        token_data = pd.DataFrame(
            {"토큰 수": [prompt_tokens, completion_tokens]},
            index=["입력(prompt)", "출력(completion)"]
        )
        st.bar_chart(token_data)

    # 진행률
    ratio = min(float(usage_summary.get("daily_limit_ratio", 0.0)), 1.0)
    st.progress(ratio, text=f"일일 한도 소진율: {int(ratio * 100)}%")