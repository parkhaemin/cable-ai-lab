"""FastAPI: same-origin page + endpoints for RAG and Agent."""
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Literal
from .agent import run_agent
from .config import ROOT, mode
from .data import load_products, product_by_id
from .rag import answer_question

app = FastAPI(title="CABLE AI 4 Week Lab", version="1.0")
app.mount("/assets", StaticFiles(directory=ROOT / "web"), name="assets")


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)
    pipeline: Literal["rag", "agent"] = "rag"
    product_id: str | None = None


@app.get("/")
def home():
    return FileResponse(ROOT / "web" / "index.html")


@app.get("/api/status")
def status():
    return {"mode":mode(), "notice":"demo는 로컬 TF-IDF·규칙, live는 OpenAI·pgvector를 사용합니다."}


@app.get("/api/products")
def products():
    return load_products()


@app.post("/api/ask")
def ask(payload: AskRequest):
    product = product_by_id(payload.product_id) if payload.product_id else None
    if payload.product_id and product is None:
        raise HTTPException(status_code=400, detail="존재하지 않는 상품 id입니다.")
    question = (f'선택 상품: {product["name"]} ({product["id"]}). ' if product else "") + payload.question
    try:
        active_mode = mode()
        return (answer_question(question, active_mode) if payload.pipeline == "rag"
                else run_agent(question, active_mode))
    except Exception as exc:
        logging.exception("AI request failed")
        raise HTTPException(status_code=503, detail=f"처리 실패: {type(exc).__name__}. 서버 로그와 설정을 확인하세요.") from exc
