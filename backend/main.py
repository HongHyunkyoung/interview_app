from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.interview_router import router as interview_router
from backend.agents_router import router as agents_router


app = FastAPI(title="면접 코치 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview_router)
app.include_router(agents_router)


