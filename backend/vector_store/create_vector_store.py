# backend/vector_store/create_vector_store.py

import shutil
from pathlib import Path
from uuid import uuid4

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from wikipediaapi import Wikipedia

from backend.core.config import SPECIES_MAP_PATHS
from backend.utils.json import load_json

species_dict = load_json(SPECIES_MAP_PATHS["species_ebird_map"])

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    encode_kwargs={"normalize_embeddings": True},
)

db_dir = "./backend/vector_store/chroma_db"
db_path = Path(db_dir)
if db_path.exists():
    shutil.rmtree(db_dir)

vector_store = Chroma(
    collection_name="bird_species_wiki_vectors",
    embedding_function=embeddings,
    persist_directory=str(db_path),
)

wiki = Wikipedia(
    user_agent="Bird-Id-Project/0.1 (mustafa.atoof@gmail.com)",
    language="en",
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
)

for bird in species_dict:
    page = wiki.page(bird)
    if not page.exists():
        print(f"Could not directly find page of {bird}, using search instead...")
        page = next(iter(wiki.search(bird, limit=1).pages.values()), None)
        print(f"Found page {page.title} using search with url: {page.fullurl}")

    if not page.exists():
        print(f"Skipping: {bird} Wikipedia page not found.")

    # Split the document, vectorize it, and store it in the vector store
    raw_text = page.text

    # Break the document into chunks
    text_chunks = text_splitter.split_text(raw_text)

    documents = []
    ids = []

    for idx, chunk in enumerate(text_chunks):
        metadata = {
            "species": page.title,
            "source": "wikipedia",
            "source_url": page.fullurl,
            "chunk_index": idx,
            "doc_type": "text",
        }

        document = Document(
            page_content=chunk,
            metadata=metadata,
            id=f"{page.title.replace(' ', '_')}_chunk_{idx}",
        )

        documents.append(document)
        ids.append(str(uuid4()))

    vector_store.add_documents(documents=documents, ids=ids)
    print("Finished building the vector database.")

results = vector_store.similarity_search_with_score(
    query="What is the lifespan of a an alder flycatcher (empidonax alnorum)?", k=5
)

print("\n")
for res in results:
    doc, score = res
    print(f"RESULT METADATA: {doc.metadata}")
    print(f"Result text: {doc.page_content}")
    print(f"SCORE: {score}")
    print("\n")
