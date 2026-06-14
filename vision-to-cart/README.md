# Vision-to-Cart: MCP Commerce Intelligence Assistant (V4)

An intelligent eyewear ordering assistant for eCommerce, coordinating image intelligence and natural language pipelines into a unified catalog intelligence and retrieval system.

## Project Structure

```
vision-to-cart/
│
├── data_services/                         # Zone 1 — Data & Services Layer
│   ├── catalog/
│   │   ├── catalog.json                   # Mock product catalog (30+ products)
│   │   ├── catalog_enriched.json          # Enriched with style taxonomy + trend scores
│   │   └── embeddings_cache/              # Pre-computed ChromaDB embedding files
│   ├── vector_store/                      # ChromaDB persistent storage directory
│   ├── redis_config/                      # Redis Docker config
│   ├── elasticsearch_config/              # Elasticsearch Docker config (optional)
│   ├── api_gateway.py                     # Unified access: validation, rate limiting, caching
│   └── data_services_router.py            # Routes data requests to correct store
│
├── mcp_server/                            # Zone 2 — MCP Server (Orchestration Layer)
│   ├── main.py                            # FastAPI app, /mcp/stream SSE endpoint, inline security guards
│   ├── orchestrator.py                    # Core pipeline sequencer
│   ├── tool_router.py                     # Dispatches tasks to tools by name
│   ├── context_manager.py                 # Session state and conversational memory
│   ├── confidence_governance.py           # Simplified: single 0.5 threshold
│   ├── error_recovery.py                  # Retry × 2 + fallback tool + graceful response
│   └── observability.py                   # Basic: console logs + /metrics JSON endpoint
│
├── tools/                                 # Zone 3 — Tools (Execution Layer)
│   ├── image_intelligence_tool.py         # Preprocessing + YOLOv8 + GPT-4o vision → StyleDNA
│   ├── nl_understanding_tool.py           # Intent extraction + Tavily/Brave web search → StyleDNA
│   ├── catalog_intelligence_tool.py       # Enrichment, style classification, vectorization & indexing
│   ├── search_retrieval_tool.py           # Hybrid search (ChromaDB vector + keyword) + filtering
│   ├── ranking_scoring_tool.py            # 5-component score + confidence check + explainability
│   ├── recommendation_tool.py             # Budget / premium / trending alternatives
│   └── pdp_cart_checkout_tool.py          # Mock PDP lookup + cart session management
│
├── intelligence/                          # Shared intelligence modules
│   ├── style_dna.py                       # StyleDNA dataclass + to_search_text() method
│   ├── normalization.py                   # Attribute normalization dictionary
│   ├── intent_schema.py                   # NL query → structured intent object
│   └── product_intelligence.py            # Embedding generation + ChromaDB ingestion
│
├── inputs/
│   ├── test_images/                       # Test images for demo scenarios
│   └── test_queries.txt                   # NL queries with expected outputs
│
├── scripts/
│   ├── ingest_catalog.py                  # One-time: embed + load catalog into ChromaDB + Redis
│   └── demo_test.py                       # Automated API calls for all demo scenarios
│
├── docker-compose.yml                     # Starts: Redis + Elasticsearch (optional)
├── .env.example                           # All env vars documented with free-tier alternatives
└── README.md                              # Setup, run instructions, planned post-hackathon extensions
```

## Setup & Installation

1. **Clone the Repository** and navigate into the `vision-to-cart` directory.
2. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn pydantic requests redis chromadb sentence-transformers ultralytics pillow rembg
   ```
3. **Configure Environment**:
   Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
4. **Start Middleware**:
   Start the Redis and Elasticsearch containers:
   ```bash
   docker compose up -d
   ```
5. **Ingest the Catalog**:
   Run the catalog ingestion script to populate ChromaDB:
   ```bash
   python scripts/ingest_catalog.py
   ```
6. **Start the MCP Server**:
   Start the FastAPI orchestration server:
   ```bash
   uvicorn mcp_server.main:app --host 0.0.0.0 --port 8000
   ```
7. **Run Demo Scenarios**:
   Verify everything runs end-to-end:
   ```bash
   python scripts/demo_test.py
   ```

## Core Workflows

### 1. Image Discovery Pipeline
* Image base64 encoded -> Preprocessing (rembg) -> YOLO crop -> LLM Feature Extraction -> Normalized StyleDNA -> Vector DB Hybrid Retrieval -> 5-Component Scoring -> Recommendations -> Done.

### 2. Natural Language (NL) Pipeline
* Chat Text -> Intent & Context Manager -> LLM Intent Schema -> Brave/Tavily Web Search (for celebrity/movie references) -> Evidence & StyleDNA Synthesis -> Hybrid Search -> Ranking -> Recommendations.
