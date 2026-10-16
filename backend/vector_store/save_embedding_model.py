from sentence_transformers import SentenceTransformer

from backend.core.config import EMBEDDING_MODEL, EMBEDDING_MODEL_DIR

model = SentenceTransformer(EMBEDDING_MODEL)

model.save(EMBEDDING_MODEL_DIR)
