# backend/routers/chat.py
import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat")
async def llm_chat():
    print("1")
