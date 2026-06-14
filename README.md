# AI 면접 코치 웹앱

## 프로젝트 개요
8주차에 만든 CLI 면접 코치를 Streamlit + FastAPI 웹앱으로 전환한 결과물입니다.
면접 질문에 대한 답변을 입력하면 AI 면접관이 SSE 스트리밍으로 실시간 피드백을 제공합니다.
멀티에이전트 구조로 질문 출제, 답변 평가, 피드백을 전문 에이전트가 분담합니다.

## 실행 방법

1. uv .venv 환경을 활성화합니다.
```powershell
.venv\Scripts\activate
```

2. FastAPI 백엔드를 8000번 포트에서 실행합니다.
```powershell
uvicorn backend.main:app --reload --port 8000
```

3. Streamlit 프론트를 8501번 포트에서 실행합니다.
```powershell
streamlit run frontend/app.py --server.port 8501
```

4. API 키는 `.env` 파일에 설정합니다. (`.env` 파일은 git에 올리지 않습니다.)
OPENAI_API_KEY=sk-proj-...

백엔드가 꺼져 있을 때: 사이드바에 "FastAPI 연결 확인 필요" 메시지가 표시됩니다.

## 핵심 기능 5개
1. SSE 스트리밍 기반 면접 대화
2. 멀티에이전트 면접 코치 (질문/평가/피드백 전문 에이전트)
3. 이력서 기반 맞춤 면접 질문 생성
4. 멀티페이지 앱 (면접 연습/이력서 분석/설정)
5. 로딩·에러·피드백·대화 검색 UX

## 기술 스택
- Python 3.10+
- Streamlit
- FastAPI
- httpx
- openai-agents
- pydantic
- python-dotenv
- uvicorn

## Day 1~5 완성 과정
- Day 1: Streamlit 면접 코치 UI 골격 + 채팅 UI
- Day 2: FastAPI 백엔드 + SSE 스트리밍 엔드포인트 + 세션 관리
- Day 3: 프론트↔백엔드 SSE 통합 + 8주차 에이전트 마운트
- Day 4: 멀티페이지 앱 구조 + 이력서 기반 질문 생성
- Day 5: UX 개선 + 에러 핸들링 + 리포트 내보내기