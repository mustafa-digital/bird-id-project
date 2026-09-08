# backend/services/rag_service.py
import logging
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from backend.core.config import CHAT_MODEL, CHROMA_DB_DIR, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    encode_kwargs={"normalize_embeddings": True},
)

db_path = Path(CHROMA_DB_DIR)

vector_store = Chroma(
    collection_name="bird_species_wiki_vectors",
    embedding_function=embeddings,
    persist_directory=str(db_path),
)

retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3},
)

llm = ChatGroq(
    model=CHAT_MODEL,
)

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a friendly chatbot with ornithology expert answering questions about bird species."
                "You are happy to help the user with their bird related questions."
                "Answer the user's query using ONLY the provided context. "
                "Do not fabricate or hallucinate information."
                "If you do not have the information based on the context to answer the question, say that you do not know the answer.\n"
                "Do not mention the given context in the response, only the response itself."
                "Format the response using plain text ONLY, no markdown."
                "Context:\n{context}"
            ),
        ),
        ("human", "{query}"),
    ]
)


async def run_chatbot(query: str):
    logger.info("Retrieving documents from vector store.")
    try:
        relevant_docs = await retriever.ainvoke(query)
    except ValueError as e:
        raise Exception(e)

    logger.info("Successfully retrieved relevant documents.")
    for doc in relevant_docs:
        logger.info(f"\nDocument ID: {doc.id}")
        logger.info(f"Document Metadata: {doc.metadata}")
    context_text = "\n\n".join([doc.page_content for doc in relevant_docs])

    formatted_prompt = await prompt_template.ainvoke(
        {"context": context_text, "query": query}
    )

    try:
        logger.info("Running inference on llm.")
        response = await llm.ainvoke(formatted_prompt)
    except ValueError as e:
        raise Exception(e)

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
