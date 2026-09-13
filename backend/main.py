import os
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from llm.groq_client import answer_query

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    question: str


class Answer(BaseModel):
    answer: str


def verify_app_password(
    x_app_password: str | None = Header(default=None, alias="X-App-Password"),
):
    expected = os.environ.get("APP_PASSWORD") or ""
    provided = x_app_password or ""
    if not expected or not secrets.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/auth")
def auth(_: None = Depends(verify_app_password)):
    return {"ok": True}


@app.post("/ask", response_model=Answer)
def ask(payload: Question, _: None = Depends(verify_app_password)):
    result = answer_query(payload.question)
    return Answer(answer=result)


@app.get("/health")
def health():
    return {"status": "ok"}
