"""
Day 3 self2 책임 메모
---------------------
- 이 파일이 담당하는 것:
  → 8주차 에이전트를 감싸고 SSE로 내보내는 백엔드 라우터

- 이 파일이 담당하지 않는 것:
  → 화면 표시, 사용자 입력 처리, AI 키 관리

- Day 3 self1의 api_client.py와의 관계:
  → 프론트 api_client.py가 이 파일의 엔드포인트를 호출한다

- 8주차 파일 재사용 원칙:
  → roles.py, tools.py, agents.py는 재작성하지 않고 import만 한다.
"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import AsyncIterator

from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Runner
from coach_agents import triage_agent, question_agent
from agents.stream_events import RawResponsesStreamEvent, RunItemStreamEvent


router = APIRouter(prefix="/agents", tags=["agents"])

class InterviewAgentRequest(BaseModel):
    """면접 에이전트 스트림 요청 값을 담습니다."""
    message: str = Field(..., description="면접 질문 텍스트")
    mode: str = Field(default="single", description="single 또는 multi")

@router.post("/stream")
async def stream_interview_agent_endpoint(
    request: InterviewAgentRequest,
) -> StreamingResponse:
    """면접 에이전트의 스트리밍 응답을 SSE로 전달합니다."""
    return StreamingResponse(
        iter_agent_events(
            run_interview_agent_stream(request.message, request.mode)
        ),
        media_type="text/event-stream"
    )


async def run_interview_agent_stream(message: str, mode: str):
    """면접 질문을 에이전트 스트림으로 실행합니다."""
    if mode == "multi":
        agent = triage_agent
    else:
        agent = question_agent

    # Runner.run_streamed로 스트림 시작
    stream_result = Runner.run_streamed(agent, message)

    async for event in stream_result.stream_events():
        yield event

async def iter_agent_events(agent_stream) -> AsyncIterator[str]:
    """에이전트 스트림 이벤트를 SSE 형식으로 정리합니다."""
    async for event in agent_stream:
    
        # 텍스트 조각 → 채팅 본문에 누적
        if isinstance(event, RawResponsesStreamEvent):
            data = event.data
            if getattr(data, "type", None) == "response.output_text.delta":
                token = data.delta  # delta는 str 그 자체
                if token:
                    payload = {"type": "token", "delta": token}
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        # 실행 항목 -> 상태 표시만
        elif isinstance(event, RunItemStreamEvent):
            payload = {"type": "status", "label":"run_item"}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        # Handoff 감지 -> 상태 표시만
        elif hasattr(event, "name") and "handoff" in str(getattr(event, "name", "")).lower():
            payload = {"type": "status", "label": "handoff"}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
    
    yield "data: [DONE]\n\n"
