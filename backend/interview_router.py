import os
from collections.abc import AsyncIterator

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from backend.sessions import (
    add_message,
    clear_session,
    create_session,
    get_history,
    get_session_role,
    set_session_role,
)


load_dotenv()

router = APIRouter(prefix="/interview", tags=["interview"])

class InterviewStreamRequest(BaseModel):
    question: str = Field(..., min_length=1, examples=["자기소개를 해 주세요."])
    answer: str = Field(..., min_length=1, examples=["안녕하세요, 저는 ..."])
    role: str = Field(default="general", examples=["technical"])
    session_id: str | None = Field(default=None)
    model: str = Field(default="gpt-4o-mini")
    
def get_interview_openai_client() -> AsyncOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="OPEN_API_KEY is not configured")
    return AsyncOpenAI(api_key=api_key)

ROLE_PROMPTS: dict[str, str] = {
    "general": "당신은 일반 면접관입니다. 지원자의 답변을 종합적으로 평가하고 개선점을 한국어로 피드백하세요.",
    "technical": "당신은 기술 면접관입니다. 지원자의 기술 역량과 문제 해결 방식을 집중 평가하고 한국어로 피드백하세요.",
    "hr": "당신은 인사 면접관입니다. 지원자의 인성, 협업 능력, 조직 적합성을 평가하고 한국어로 피드백하세요.",
}

async def interview_event_generator(
    request: InterviewStreamRequest,
)-> AsyncIterator[str]:
    """면접 코치 피드백을 SSE data 이벤트로 스트리밍합니다."""
    client = get_interview_openai_client()
    system_prompt = ROLE_PROMPTS.get(request.role, ROLE_PROMPTS["general"])
    
    user_content = (
        f"[면접 질문]\n{request.question}\n\n"
        f"[지원자 답변]\n{request.answer}\n\n"
        "위 답변을 면접관 역할에 맞게 평가하고 개선 피드백을 제공해 주세요."
    )

    stream = await client.chat.completions.create(
        model=request.model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        stream=True,
    )
    
    async for chunk in stream:
        delta = chunk.choices[0].delta
        token = delta.content or ""
                
        if not token:
            continue
        
        yield f"data: {token}\n\n"
    yield "data: [DONE]\n\n"
    
@router.post("/stream")
async def interview_stream(request: InterviewStreamRequest) -> StreamingResponse:
    return StreamingResponse(
        interview_event_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
    
class SessionCreateRequest(BaseModel):
    role: str = Field(default="general", description="초기 면접관 유형")

class SessionCreateResponse(BaseModel):
    session_id: str
    role: str
    
@router.post("/session/create", response_model=SessionCreateResponse)
async def create_interview_session(
    body: SessionCreateRequest,
) -> SessionCreateResponse:
    """새 면접 세션을 생성하고 UUID session_id를 반환합니다."""
    session_id = create_session(body.role)
    return SessionCreateResponse(session_id=session_id, role=body.role)
    
class HistoryResponse(BaseModel):
    session_id: str
    messages: list[dict[str, str]]
    role: str
    message_count: int
    
@router.get("/session/{session_id}/history", response_model=HistoryResponse)
async def get_interview_history(session_id: str) -> HistoryResponse:
    """세션 ID로 면접 이력을 조회합니다."""
    try:
        messages = get_history(session_id)
        role = get_session_role(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="session not found")
    
    return HistoryResponse(
        session_id=session_id,
        messages=messages,
        role=role,
        message_count=len(messages),
    )
    
ALLOWED_ROLES = {"general", "technical", "hr"}

class RoleUpdateRequest(BaseModel):
    role: str = Field(..., description="변경할 면접관 유형 (general, technical, hr)")

class RoleUpdateResponse(BaseModel):
    session_id: str
    role: str
    message: str
    
@router.patch("/session/{session_id}/role", response_model=RoleUpdateResponse)
async def update_interview_role(
    session_id: str,
    body: RoleUpdateRequest,
) -> RoleUpdateResponse:
    """세션의 면접관 유형을 변경합니다."""
    # 허용되지 않은 유형이면 400 오류
    if body.role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"허용되지 않는 role: {body.role}. 허용값: {ALLOWED_ROLES}",
        )
    # 없는 세션이면 404 오류
    try:
        set_session_role(session_id, body.role)
    except KeyError:
        raise HTTPException(status_code=404, detail="session not found")
    return RoleUpdateResponse(
        session_id=session_id,
        role=body.role,
        message=f"면접관 유형이 {body.role}으로 변경되었습니다."
    )