from __future__ import annotations
from datetime import datetime
from typing import Any
import streamlit as st


def build_interview_report(
    conversation: dict[str, Any],
    usage_summary: dict[str, Any],
    feedback_summary: dict[str, int] | None = None,
) -> str:
    """선택된 면접 세션을 마크다운 리포트 문자열로 만든다."""
    lines = []

    # 제목
    title = conversation.get("title", "면접 세션")
    lines.append(f"# 면접 리포트 - {title}")
    lines.append(f"- 생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # 대화 목록
    lines.append("## 면접 대화 기록")
    lines.append("| # | 역할 | 내용 |")
    lines.append("|---|---|---|")

    for i, msg in enumerate(conversation.get("messages", []), start=1):
        content = msg.get("content", "")[:60].replace("|", "/")
        role = msg.get("role", "")
        lines.append(f"| {i} | {role} | {content}... |")

    lines.append("")

    # 피드백 요약
    lines.append("## 피드백 요약")
    if feedback_summary:
        lines.append(f"- 👍 좋아요: {feedback_summary.get('up', 0)}개")
        lines.append(f"- 👎 싫어요: {feedback_summary.get('down', 0)}개")
    else:
        lines.append("- 피드백 없음")

    lines.append("")

    # 사용량 요약
    lines.append("## 사용량 요약")
    lines.append(f"- 총 요청 수: {usage_summary.get('request_count', 0)}회")
    lines.append(f"- 총 토큰: {usage_summary.get('total_tokens', 0):,}")

    lines.append("")

    # 9주차 완성 기능
    lines.append("## 9주차 완성 기능")
    lines.append("- ✅ Streamlit + FastAPI SSE 스트리밍")
    lines.append("- ✅ 멀티에이전트 면접 코치")
    lines.append("- ✅ 이력서 기반 질문 생성")
    lines.append("- ✅ 멀티페이지 앱 구조")
    lines.append("- ✅ UX 개선 (로딩/에러/피드백/검색)")

    return "\n".join(lines)


def render_report_download(
    session_id: str,
    conversation: dict[str, Any] | None,
    usage_summary: dict[str, Any],
) -> None:
    """리포트 생성 조건을 확인하고 다운로드 버튼을 표시한다."""
    if not conversation:
        st.info("리포트를 만들 세션을 먼저 선택하세요.")
        return

    messages = conversation.get("messages", [])
    if not messages:
        st.warning("선택한 세션에 메시지가 없습니다.")
        return

    report_md = build_interview_report(conversation, usage_summary)

    st.download_button(
        label="📥 리포트 다운로드",
        data=report_md,
        file_name=f"interview_{session_id}.md",
        mime="text/markdown",
    )