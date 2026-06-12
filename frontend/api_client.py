from __future__ import annotations
import os
from collections.abc import Iterator
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

def get_backend_url() -> str:
    """면접 코치 FastAPI 백엔드 주소를 환경변수 또는 기본값으로 가져옵니다."""
    return os.getenv("BACKEND_URL","http://localhost:8000")

def post_interview_message(message: str) -> dict[str, Any]:
    """면접 코치 백엔드에 일반 응답 요청을 보냅니다."""
    with httpx.Client(base_url=get_backend_url(), timeout=10.0) as client:
        response = client.post("/chat", json={"message":message})
        response.raise_for_status()
        return response.json()
    
def stream_interview_message(
    question: str,
    answer: str,
    role: str = "general",
    session_id: str | None= None,
) -> Iterator[str]:
    """면접 코치 백엔드의 SSE 응답을 순서대로 전달합니다."""
    payload={
        "question":question,
        "answer": answer,
        "role": role,
        "session_id": session_id,
    }
    url = f"{get_backend_url()}/interview/stream"
    
    with httpx.stream("POST", url, json=payload, timeout=30.0) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            # 빈 줄 건너뜀
            if not line:
                continue
            # data: 접두사 없는 줄 건너뜀
            if not line.startswith("data:"):
                continue
            token = line[5:].strip()
            # 종료 신호 확인
            if token == "[DONE]":
                break
            yield token

def render_streaming_answer(
    placeholder: Any,
    question: str,
    answer: str,
    role: str = "general",
    session_id: str | None = None,
) -> str:
    """스트리밍 토큰을 누적해 면접 코치 답변을 화면에 표시합니다."""
    full_text = ""
    
    for token in stream_interview_message(question, answer, role, session_id):
        full_text += token
        placeholder.markdown(full_text)
        
    return full_text