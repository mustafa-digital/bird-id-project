# backend/core/rag_config.py

import logging

from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from backend.core.config import (
    CHAT_MODEL,
    CHROMA_DB_DIR,
    EMBEDDING_MODEL_DIR,
    TOP_K_DOCUMENTS,
)
from backend.core.rag_prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def init_rag_service():

    # Load hugging face embeddings model
    try:
        logger.info("Loading embedding model...")
        embeddings = HuggingFaceEmbeddings(
            model_name=str(EMBEDDING_MODEL_DIR),
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info("Loaded embedding model")
    except Exception as e:
        raise RuntimeError(f"Error: Could not load embedding model: {e}")

    # Load the chroma vector database
    try:
        logger.info("Loading chroma database...")
        vector_store = Chroma(
            collection_name="bird_species_wiki_vectors",
            embedding_function=embeddings,
            persist_directory=str(CHROMA_DB_DIR),
        )
        logger.info("Loaded chroma database")
    except Exception as e:
        raise RuntimeError(f"Error: Could not load chroma database: {e}")

    # Initialize vector store retriever object
    try:
        logger.info("Initializing vector store retriever...")
        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": TOP_K_DOCUMENTS,
                "fetch_k": 2 * TOP_K_DOCUMENTS,
                "lambda_mult": 0.5,
            },
        )
        logger.info("Initialized vector store retriever")
    except Exception as e:
        raise RuntimeError(f"Error: Could not initialize retriever object: {e}")

    return retriever


def init_chat_model():
    try:
        logger.info("Initializing Groq inference API client")
        chat_model = ChatGroq(
            model=CHAT_MODEL,
        )
        logger.info("Groq API client initialized")
    except Exception as e:
        raise RuntimeError(f"Error initializing Groq inference API: {e}")
    return chat_model


def init_chat_prompt_template():
    try:
        logger.info("Initializing chat prompt template...")
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                (
                    "ai",
                    "Hello, I am your ornithology assistant. Ask me anything about birds!",
                ),
                ("placeholder", "{conversation}"),
                ("human", "<user_query>\n{query}\n</user_query>"),
            ]
        )
        logger.info("Chat prompt template initialization complete")
    except Exception as e:
        raise RuntimeError(f"Error: Could not set up prompt template: {e}")
    return prompt_template
