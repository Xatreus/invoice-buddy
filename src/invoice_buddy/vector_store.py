from pathlib import Path
from typing import Any

import chromadb


VECTOR_DB_PATH = Path("data/chroma")
COLLECTION_NAME = "invoice_documents"


def get_vector_client(
    path: str | Path = VECTOR_DB_PATH,
) -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=str(path))


def get_collection(
    path: str | Path = VECTOR_DB_PATH,
):
    client = get_vector_client(path)

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def add_documents(
    documents: list[str],
    embeddings: list[list[float]],
    ids: list[str],
    metadatas: list[dict[str, Any]],
    path: str | Path = VECTOR_DB_PATH,
) -> None:
    if not (len(documents) == len(embeddings) == len(ids) == len(metadatas)):
        raise ValueError(
            "documents, embeddings, ids, and metadatas must have the same length."
        )

    if not documents:
        return

    collection = get_collection(path)

    collection.upsert(
        documents=documents,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas,
    )


def search_documents(
    query_embedding: list[float],
    n_results: int = 5,
    path: str | Path = VECTOR_DB_PATH,
    where: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if n_results <= 0:
        raise ValueError("n_results must be greater than zero.")

    collection = get_collection(path)

    if collection.count() == 0:
        return []

    query_arguments = {
        "query_embeddings": [query_embedding],
        "n_results": min(
            n_results,
            collection.count(),
        ),
        "include": [
            "documents",
            "metadatas",
            "distances",
        ],
    }

    if where is not None:
        query_arguments["where"] = where

    results = collection.query(**query_arguments)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    ids = results["ids"][0]

    return [
        {
            "id": document_id,
            "document": document,
            "metadata": metadata,
            "distance": distance,
        }
        for document_id, document, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
        )
    ]


def delete_invoice_documents(
    invoice_number: str,
    path: str | Path = VECTOR_DB_PATH,
) -> None:
    collection = get_collection(path)

    collection.delete(
        where={"invoice_number": invoice_number},
    )
