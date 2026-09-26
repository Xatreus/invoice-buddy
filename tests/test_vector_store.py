from pathlib import Path

import pytest

from invoice_buddy.vector_store import (
    add_documents,
    delete_invoice_documents,
    search_documents,
)


def test_add_and_search_documents(tmp_path: Path):
    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    documents = [
        "AWS cloud hosting services",
        "Office furniture and desks",
    ]

    ids = [
        "INV-001-chunk-0",
        "INV-002-chunk-0",
    ]

    metadatas = [
        {
            "invoice_number": "INV-001",
            "vendor": "AWS",
            "chunk_index": 0,
        },
        {
            "invoice_number": "INV-002",
            "vendor": "Office Depot",
            "chunk_index": 0,
        },
    ]

    add_documents(
        documents=documents,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas,
        path=tmp_path,
    )

    results = search_documents(
        query_embedding=[1.0, 0.0, 0.0],
        n_results=1,
        path=tmp_path,
    )

    assert len(results) == 1
    assert results[0]["id"] == "INV-001-chunk-0"
    assert results[0]["metadata"]["vendor"] == "AWS"


def test_search_empty_collection(tmp_path: Path):
    results = search_documents(
        query_embedding=[1.0, 0.0, 0.0],
        path=tmp_path,
    )

    assert results == []


def test_add_documents_rejects_mismatched_lengths(tmp_path: Path):
    with pytest.raises(ValueError):
        add_documents(
            documents=["one", "two"],
            embeddings=[[1.0, 0.0, 0.0]],
            ids=["id-1", "id-2"],
            metadatas=[
                {"invoice_number": "INV-001"},
                {"invoice_number": "INV-002"},
            ],
            path=tmp_path,
        )


def test_search_rejects_invalid_result_count(tmp_path: Path):
    with pytest.raises(ValueError):
        search_documents(
            query_embedding=[1.0, 0.0, 0.0],
            n_results=0,
            path=tmp_path,
        )


def test_delete_invoice_documents(tmp_path: Path):
    add_documents(
        documents=[
            "AWS cloud hosting",
            "Office supplies",
        ],
        embeddings=[
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        ids=[
            "INV-001-chunk-0",
            "INV-002-chunk-0",
        ],
        metadatas=[
            {
                "invoice_number": "INV-001",
                "vendor": "AWS",
            },
            {
                "invoice_number": "INV-002",
                "vendor": "Office Depot",
            },
        ],
        path=tmp_path,
    )

    delete_invoice_documents(
        invoice_number="INV-001",
        path=tmp_path,
    )

    results = search_documents(
        query_embedding=[1.0, 0.0, 0.0],
        n_results=5,
        path=tmp_path,
    )

    assert len(results) == 1
    assert results[0]["id"] == "INV-002-chunk-0"
