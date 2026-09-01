import asyncio
from collections.abc import Mapping
from typing import Any

import pytest

from app.adapters.product_identity.opensearch import (
    OpenSearchAdapter,
    OpenSearchEvidenceContractError,
    build_product_evidence_index_mapping,
    build_product_evidence_search_pipeline,
)
from app.domain.product_identity import EvidenceModality


class FakeEmbedder:
    async def embed(self, text: str) -> list[float]:
        assert text
        return [0.1, 0.2, 0.3]


class RecordingOpenSearchClient:
    def __init__(self, response: Mapping[str, Any]) -> None:
        self.response = response
        self.index: str | None = None
        self.body: Mapping[str, Any] | None = None
        self.params: Mapping[str, str] | None = None

    async def search(
        self,
        *,
        index: str,
        body: Mapping[str, Any],
        params: Mapping[str, str] | None = None,
    ) -> Mapping[str, Any]:
        self.index = index
        self.body = body
        self.params = params
        return self.response


def valid_response() -> dict[str, Any]:
    return {
        "hits": {
            "hits": [
                {
                    "_id": "ev-product-code",
                    "_source": {
                        "evidence_id": "ev-product-code",
                        "document_id": "abb-official",
                        "page": 21,
                        "modality": "text",
                        "text": "S203-C16 16 A",
                        "asset_uri": None,
                        "content_hash": "abc123",
                    },
                }
            ]
        }
    }


def test_builds_hybrid_query_and_maps_hits_to_evidence() -> None:
    client = RecordingOpenSearchClient(valid_response())
    adapter = OpenSearchAdapter(
        client=client,
        embedder=FakeEmbedder(),
        candidate_pool=100,
    )

    result = asyncio.run(
        adapter.search(
            "ABB S203-C16 автомат 3P 16A",
            document_ids=("abb-official",),
            limit=10,
        )
    )

    assert len(result) == 1
    assert result[0].evidence_id == "ev-product-code"
    assert result[0].modality is EvidenceModality.TEXT
    assert client.index == "product_evidence"
    assert client.params == {"search_pipeline": "product-evidence-hybrid"}
    assert client.body is not None

    hybrid = client.body["query"]["hybrid"]  # type: ignore[index]
    queries = hybrid["queries"]
    assert len(queries) == 2

    lexical = queries[0]["bool"]
    assert lexical["filter"] == [
        {"terms": {"document_id": ["abb-official"]}}
    ]
    assert {"terms": {"identifiers": ["S203-C16", "3P", "16A"]}} in lexical[
        "should"
    ]

    vector = queries[1]["knn"]["embedding"]
    assert vector["vector"] == [0.1, 0.2, 0.3]
    assert vector["k"] == 100
    assert vector["filter"] == {
        "terms": {"document_id": ["abb-official"]}
    }


def test_rejects_malformed_opensearch_evidence_document() -> None:
    client = RecordingOpenSearchClient(
        {
            "hits": {
                "hits": [
                    {
                        "_id": "broken",
                        "_source": {
                            "document_id": "abb-official",
                        },
                    }
                ]
            }
        }
    )
    adapter = OpenSearchAdapter(client=client, embedder=FakeEmbedder())

    with pytest.raises(OpenSearchEvidenceContractError):
        asyncio.run(
            adapter.search(
                "ABB S203-C16",
                document_ids=("abb-official",),
            )
        )


def test_evidence_index_mapping_supports_filtered_hybrid_search() -> None:
    mapping = build_product_evidence_index_mapping(1024)
    properties = mapping["mappings"]["properties"]
    vector = properties["embedding"]

    assert mapping["settings"]["index"]["knn"] is True
    assert properties["document_id"] == {"type": "keyword"}
    assert properties["identifiers"] == {"type": "keyword"}
    assert vector["type"] == "knn_vector"
    assert vector["dimension"] == 1024
    assert vector["space_type"] == "cosinesimil"
    assert vector["method"]["engine"] == "lucene"


def test_search_pipeline_uses_equal_weight_normalized_scores() -> None:
    pipeline = build_product_evidence_search_pipeline()
    processor = pipeline["phase_results_processors"][0]["normalization-processor"]

    assert processor["normalization"] == {"technique": "min_max"}
    assert processor["combination"] == {"technique": "arithmetic_mean"}
