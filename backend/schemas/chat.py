# backend/schemas/chat.py

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    request_id: str
    llm_response: str
