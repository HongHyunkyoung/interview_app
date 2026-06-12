import os
from collections.abc import AsyncIterator

from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

load_dotenv()

router = APIRouter(prefix="/interview", tags=["interview"])
