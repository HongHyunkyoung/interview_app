from fastapi import FastAPI
from interview_app.backend.interview_router import router


app = FastAPI(title="면접 코치 API")

app.include_router(router)


