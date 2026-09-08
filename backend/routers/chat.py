# backend/routers/chat.py
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from backend.core.config import MAX_QUERY_SIZE
from backend.core.exceptions import InferenceError, RetrievalError
from backend.core.request_context import get_request_id
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.rag_service import run_chatbot

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def llm_chat(request_body: ChatRequest, request_id=Depends(get_request_id)):
    user_query = request_body.query
    if not user_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty."
        )

    if len(user_query) > MAX_QUERY_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User query exceeds maximum length of {MAX_QUERY_SIZE}.",
        )

        logger.info(
            "Received user chat request.", extra={"query_length": len(user_query)}
        )

    try:
        response = await run_chatbot(user_query)
        return ChatResponse(request_id=request_id, llm_response=response)
    except RetrievalError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except InferenceError as e:
        raise HTTPException(status_code=503, detail=str(e))
