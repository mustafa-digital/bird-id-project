# backend/tests/test_llm_chat.py

from fastapi import status
from fastapi.testclient import TestClient

from backend.core.config import MAX_QUERY_SIZE
from backend.main import app

client = TestClient(app)


def test_query_too_large():
    query = "*" * (MAX_QUERY_SIZE + 1)
    response = client.post("/chat", json={"query": query})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_empty_query():
    query = ""
    response = client.post("/chat", json={"query": query})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_no_query_sent():
    response = client.post("/chat")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_accepted_query():
    query = "What is the lifespan of an american robin (turdus migratorius)?"
    response = client.post("/chat", json={"query": query})

    assert response.status_code == status.HTTP_200_OK
    assert "llm_response" in response.json()
    assert len(response.json()["llm_response"]) > 0
