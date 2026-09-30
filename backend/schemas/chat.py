# backend/schemas/chat.py

from pydantic import BaseModel, Field

from backend.core.config import MAX_QUERY_SIZE


class ChatRequest(BaseModel):
    query: str = Field(
        description="User's chat query.", min_length=1, max_length=MAX_QUERY_SIZE
    )
    message_history: list = Field(
        default_factory=list,
        description="List of previous messages in the conversation. Each message is a dictionary with 'role' and 'message' keys.",
    )


class ChatResponse(BaseModel):
    request_id: str
    llm_response: str
