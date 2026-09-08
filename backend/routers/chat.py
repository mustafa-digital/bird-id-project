# backend/routers/chat.py
import logging

from fastapi import APIRouter, Depends, HTTPException

from backend.core.request_context import get_request_id
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.rag_service import run_chatbot

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def llm_chat(request_body: ChatRequest, request_id=Depends(get_request_id)):
    logger.info("Received user chat request.")
    user_query = request_body.query

    try:
        response = await run_chatbot(user_query)
        print(response)
        return ChatResponse(request_id=request_id, llm_response=response)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
