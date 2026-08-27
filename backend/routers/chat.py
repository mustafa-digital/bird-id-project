# backend/routers/chat.py
import logging

from fastapi import APIRouter, HTTPException

from backend.services.rag_service import query_wikidata_vector_api

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat")
async def llm_chat():
    user_query = "what is the lifespan of an american robin (turdus migratorius)?"
    try:
        results = query_wikidata_vector_api(query_string=user_query)
        print(results)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
