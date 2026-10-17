# backend/services/rag_service.py
import logging
import time

from langchain_core.exceptions import LangChainException
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_groq import ChatGroq

from backend.core.exceptions import InferenceError, RetrievalError

logger = logging.getLogger(__name__)


async def run_chatbot(
    retriever: VectorStoreRetriever,
    chat_model: ChatGroq,
    prompt_template: ChatPromptTemplate,
    query: str,
    message_history: list | None = None,
) -> str:
    logger.info(f"Received message history: {message_history}")
    logger.info("Retrieving documents from vector store.")

    logger.info(
        "Received user chat request.",
        extra={"query_length": len(query), "query": query},
    )

    try:
        start_time = time.perf_counter()
        relevant_docs = await retriever.ainvoke(query)
        rag_time = (time.perf_counter() - start_time) * 1000
    except LangChainException as e:
        raise RetrievalError(e)

    if relevant_docs:
        logger.info(
            f"Successfully retrieved relevant documents. Number of docs: {len(relevant_docs)}"
            f"  Retrieval Time: {rag_time:.2f}ms"
        )
    else:
        logger.info("No relevant documents were found.")
    for doc in relevant_docs:
        logger.info(f"\nDocument ID: {doc.id}")
        logger.info(f"Document Metadata: {doc.metadata}")
    context_text = "\n\n".join([doc.page_content for doc in relevant_docs])

    if message_history:
        logger.info(
            f"Formatting message history for prompt. Number of messages: {len(message_history)}"
        )
        formatted_messages = [(msg["role"], msg["message"]) for msg in message_history]
        formatted_prompt = await prompt_template.ainvoke(
            {
                "context": context_text,
                "query": query,
                "conversation": formatted_messages,
            }
        )
    else:
        formatted_prompt = await prompt_template.ainvoke(
            {"context": context_text, "query": query, "conversation": []}
        )

    try:
        logger.info("Running inference on llm.")
        response = await chat_model.ainvoke(formatted_prompt)
    except LangChainException as e:
        raise InferenceError(e)

    logger.info(response.response_metadata)

    logger.info("Returning llm response.")
    return response.content


"""
async def search_documentation(query: str) -> list[Document]:
    results = retriever.ainvoke(query)

    return results

"""

"""

VECTOR_API_URL = "https://wd-vectordb.wmcloud.org/item/query/"
headers = {
    "User-Agent": "Bird-Id-Project/0.1 (mustafa.atoof@gmail.com)",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
}

def query_wikidata_vector_api(query_string: str):
    if len(query_string) < 1:
        return "Short string"

    logger.info(f"Received user query: {query_string}")

    params = {
        "query": query_string,
        "lang": "en",
        "K": 3,
        # "return_vectors": "true",
        # "rerank": "false",
    }
    # WIKIDATA_API_URL = f"https://wd-vectordb.wmcloud.org/item/query/?query={query_string}&lang=en&K=3&rerank=false&return_vectors=true"

    response = requests.get(VECTOR_API_URL, params=params, headers=headers)
    print(f"Raw Response: {response.text}")
    if response.status_code != 200:
        # print(response.json())
        logger.error(f"Error when requesting from WikiData API: {response.status_code}")
        raise ValueError(
            f"Error when requesting from WikiData API: {response.status_code}"
        )

    results = response.json()
    if not results:
        print("No matching Wikidata entities found.")
        return

    return results

"""
