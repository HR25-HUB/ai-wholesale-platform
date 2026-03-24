
# AI Wholesale Platform Production Repo

Enterprise-scale reference architecture for an AI-powered wholesale automation platform.

Stack
- Python
- Pydantic / PydanticAI
- Prefect orchestration
- Redpanda event bus
- OpenSearch vector search
- Streamlit dashboards
- Bitrix24 integration
- Docker infrastructure

Core Domains
- Data Factory
- RFQ Automation
- Product Brain
- Procurement Engine
- Pricing Intelligence
- Knowledge Graph

Run (local dev):

docker compose up
python scripts/bootstrap_opensearch.py
