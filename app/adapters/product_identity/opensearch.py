from collections.abc import Mapping
from typing import Any, Protocol

from pydantic import ValidationError

from app.application.product_identity.ports import EmbeddingPort
from app.domain.product_identity.models import Evidence


class OpenSearchClientPort(Protocol):
    async def search(
        self,
        *,
        index: str,
        body: Mapping[str, Any],
        params: Mapping[str, str] | None = None,
    ) -> Mapping[str, Any]: ...


class OpenSearchEvidenceContractError(RuntimeError):
    pass


def build_product_evidence_index_mapping(dimension: int) -> dict[str, Any]:
    if dimension < 1:
        raise ValueError("embedding dimension must be positive")

    return {
        "settings": {
            "index": {
                "knn": True,
            }
        },
        "mappings": {
            "properties": {
                "evidence_id": {"type": "keyword"},
                "document_id": {"type": "keyword"},
                "page": {"type": "integer"},
                "modality": {"type": "keyword"},
                "text": {"type": "text"},
                "identifiers": {"type": "keyword"},
                "asset_uri": {"type": "keyword", "index": False},
                "content_hash": {"type": "keyword"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": dimension,
                    "space_type": "cosinesimil",
                    "method": {
                        "name": "hnsw",
                        "engine": "lucene",
                    },
                },
            }
        },
    }


def build_product_evidence_search_pipeline() -> dict[str, Any]:
    return {
        "description": "Normalize BM25 and vector scores for product evidence",
        "phase_results_processors": [
            {
                "normalization-processor": {
                    "normalization": {"technique": "min_max"},
                    "combination": {
                        "technique": "arithmetic_mean",
                    },
                }
            }
        ],
    }


class OpenSearchAdapter:
    def __init__(
        self,
        *,
        client: OpenSearchClientPort,
        embedder: EmbeddingPort,
        index_name: str = "product_evidence",
        search_pipeline: str = "product-evidence-hybrid",
        candidate_pool: int = 50,
    ) -> None:
        if candidate_pool < 1:
            raise ValueError("candidate_pool must be positive")
        self._client = client
        self._embedder = embedder
        self._index_name = index_name
        self._search_pipeline = search_pipeline
        self._candidate_pool = candidate_pool

    async def search(
        self,
        query: str,
        *,
        document_ids: tuple[str, ...],
        limit: int = 10,
    ) -> list[Evidence]:
        if limit < 1:
            raise ValueError("limit must be positive")
        if not document_ids:
            return []

        query_vector = await self._embedder.embed(query)
        if not query_vector:
            raise ValueError("embedding vector must not be empty")

        candidate_pool = max(limit, self._candidate_pool)
        filters = {"terms": {"document_id": list(document_ids)}}
        identifier_candidates = self._identifier_candidates(query)

        lexical_should: list[dict[str, Any]] = [
            {
                "match": {
                    "text": {
                        "query": query,
                    }
                }
            }
        ]
        if identifier_candidates:
            lexical_should.append(
                {
                    "terms": {
                        "identifiers": identifier_candidates,
                    }
                }
            )

        body: dict[str, Any] = {
            "size": candidate_pool,
            "_source": {"excludes": ["embedding", "identifiers"]},
            "query": {
                "hybrid": {
                    "queries": [
                        {
                            "bool": {
                                "filter": [filters],
                                "should": lexical_should,
                                "minimum_should_match": 1,
                            }
                        },
                        {
                            "knn": {
                                "embedding": {
                                    "vector": query_vector,
                                    "k": candidate_pool,
                                    "filter": filters,
                                }
                            }
                        },
                    ]
                }
            },
        }

        response = await self._client.search(
            index=self._index_name,
            body=body,
            params={"search_pipeline": self._search_pipeline},
        )
        return self._parse_hits(response, limit=limit)

    @staticmethod
    def _identifier_candidates(query: str) -> list[str]:
        punctuation = ",.;:()[]{}<>\"'"
        tokens = [token.strip(punctuation) for token in query.split()]
        return [
            token
            for token in tokens
            if token and any(character.isdigit() for character in token)
        ]

    @staticmethod
    def _parse_hits(
        response: Mapping[str, Any],
        *,
        limit: int,
    ) -> list[Evidence]:
        hits_container = response.get("hits")
        if not isinstance(hits_container, Mapping):
            raise OpenSearchEvidenceContractError("response.hits must be an object")

        hits = hits_container.get("hits")
        if not isinstance(hits, list):
            raise OpenSearchEvidenceContractError("response.hits.hits must be a list")

        evidence: list[Evidence] = []
        for hit in hits[:limit]:
            if not isinstance(hit, Mapping):
                raise OpenSearchEvidenceContractError("search hit must be an object")
            source = hit.get("_source")
            if not isinstance(source, Mapping):
                raise OpenSearchEvidenceContractError("search hit _source must be an object")
            try:
                evidence.append(Evidence.model_validate(source))
            except ValidationError as error:
                hit_id = hit.get("_id", "unknown")
                raise OpenSearchEvidenceContractError(
                    f"invalid evidence document in OpenSearch hit {hit_id}"
                ) from error

        return evidence
