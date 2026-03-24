
from opensearchpy import OpenSearch
import json

client = OpenSearch("http://localhost:9200")

with open("opensearch/products_index.json") as f:
    body = json.load(f)

client.indices.create(index="products", body=body, ignore=400)

print("OpenSearch index initialized")
