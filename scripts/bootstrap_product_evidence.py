import os

from opensearchpy import OpenSearch

from app.adapters.product_identity.opensearch import (
    build_product_evidence_index_mapping,
    build_product_evidence_search_pipeline,
)


def _embedding_dimension() -> int:
    raw_value = os.getenv("EVIDENCE_EMBEDDING_DIMENSION")
    if raw_value is None:
        raise RuntimeError("EVIDENCE_EMBEDDING_DIMENSION must be configured")

    dimension = int(raw_value)
    if dimension < 1:
        raise RuntimeError("EVIDENCE_EMBEDDING_DIMENSION must be positive")
    return dimension


def main() -> None:
    opensearch_url = os.getenv("OPENSEARCH_URL", "http://localhost:9200")
    index_name = os.getenv("PRODUCT_EVIDENCE_INDEX", "product_evidence")
    search_pipeline = os.getenv(
        "PRODUCT_EVIDENCE_SEARCH_PIPELINE",
        "product-evidence-hybrid",
    )

    client = OpenSearch(opensearch_url)
    mapping = build_product_evidence_index_mapping(_embedding_dimension())

    if not client.indices.exists(index=index_name):
        client.indices.create(index=index_name, body=mapping)

    client.transport.perform_request(
        "PUT",
        f"/_search/pipeline/{search_pipeline}",
        body=build_product_evidence_search_pipeline(),
    )

    print(
        "Product evidence OpenSearch resources initialized: "
        f"index={index_name}, pipeline={search_pipeline}"
    )


if __name__ == "__main__":
    main()
