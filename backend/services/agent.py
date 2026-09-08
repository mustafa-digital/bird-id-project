# backend/services/agent.py

from langchain.chat_models import init_chat_model

from backend.core.config import CHAT_MODEL

model = init_chat_model(model=CHAT_MODEL)
