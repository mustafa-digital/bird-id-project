# backend/services/rag_service.py
import logging

import requests

VECTOR_API_URL = "https://wd-vectordb.wmcloud.org/item/query/"
headers = {
    "User-Agent": "Bird-Id-Project/0.1 (mustafa.atoof@gmail.com)",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
}

logger = logging.getLogger(__name__)


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
