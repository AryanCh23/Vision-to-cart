# Vision-to-Cart: MCP Commerce Intelligence
## Complete Implementation Plan — Hackathon 3.0 (V4 — Simplified for Hackathon)
### Scope: Hackathon · Timebox: 8 Hours

---

# Index

1. [Project Overview](#1-project-overview)
2. [Model Selection Guide](#2-model-selection-guide)
3. [Technology Stack](#3-technology-stack)
4. [Repository Structure](#4-repository-structure)
5. [Core Architecture — V4](#5-core-architecture--v4)
6. [Phase 0 — Setup & Scaffolding (Hour 0–1)](#6-phase-0--setup--scaffolding-hour-01)
7. [Phase 1 — Data & Services Layer (Hour 0–1, parallel)](#7-phase-1--data--services-layer-hour-01-parallel)
8. [Phase 2 — MCP Server & Tool Contracts (Hour 1–2)](#8-phase-2--mcp-server--tool-contracts-hour-12)
9. [Phase 3 — Catalog Intelligence Service (Hour 2–3)](#9-phase-3--catalog-intelligence-service-hour-23)
10. [Phase 4 — Image Discovery Pipeline (Hour 3–5)](#10-phase-4--image-discovery-pipeline-hour-35)
11. [Phase 5 — Natural Language Discovery Pipeline (Hour 5–6.5)](#11-phase-5--natural-language-discovery-pipeline-hour-565)
12. [Phase 6 — Streaming & Cross-Cutting Layers (Hour 6.5–7.5)](#12-phase-6--streaming--cross-cutting-layers-hour-6575)
13. [Phase 7 — Testing & Demo (Hour 7.5–8)](#13-phase-7--testing--demo-hour-758)
14. [Remaining Risks & Mitigations](#14-remaining-risks--mitigations)
15. [Evaluation Checklist](#15-evaluation-checklist)

---



## Objective

Build an **MCP-based intelligent ordering assistant** for Magrabi's eCommerce platform that:

- Accepts **image uploads** and matches them to products via visual similarity — handling real-world photos, not just clean catalog images
- Accepts **natural language queries** including celebrity references, event names, and vague style descriptions, and resolves them to specific products
- Orchestrates all intelligence through a clean, demonstrable **MCP client-server architecture** with modular tools
- Delivers an **engaging, progressive UX** that communicates every processing step to the user in real time
- Builds towards a **production-quality system** that goes beyond a hackathon MVP

## What the Judges Are Looking For

| Evaluation Dimension | What "Impressive" Looks Like |
|---|---|
| MCP Architecture (20 marks) | Real separation: client never touches tools, orchestrator is the only brain |
| Image Intelligence (20 marks) | Handles noise, backgrounds, partial visibility — not just clean catalog photos |
| NL Understanding (15 marks) | Resolves actor + movie + product type → real product via web evidence |
| Product Mapping (15 marks) | Results are relevant, ranked, explainable, and link to a real PDP |
| UX Engagement (15 marks) | No blank screens; every second of processing is communicated to the user |
| Code Quality (10 marks) | Each module is independent, testable, and follows clear contracts |
| Demo Clarity (5 marks) | Video covers all flows cleanly; intelligence is visible, not hardcoded |
| Bonus (up to +10) | Streaming, multi-image, recommendations, voice/animation |

## V4 Changes Over V3

V4 is the **approved hackathon architecture**. Three structural changes from V3:

| Change | V3 | V4 |
|---|---|---|
| **Data Layer** | Implicit (catalog.json only) | Explicit Zone 1 — Data & Services Layer with API Gateway, Vector DB, Redis, Elasticsearch |
| **Frontend** | React client in scope | Removed from 8-hour scope — demo via API test script |
| **Tool set** | 5 tools + separate web search | 6 consolidated tools — web search merged into NL Understanding Tool |

**Out of Scope (Documented, Not Implemented):**
- Feedback & Learning Loop
- Advanced V3 Additions (Observability Dashboards, Embedding Drift Mitigation, Security Enhancements beyond basic)
- Full Confidence Routing Tree (High/Medium/Low)

> **Post-Hackathon Note:** All out-of-scope layers are fully specified in this document and should be implemented after the hackathon as the platform matures toward production.

---

# 2. Model Selection Guide

This section defines which AI models to use, why, and what is available at each budget tier. Choose your tier before starting Phase 0 so the correct API keys are in `.env` from the beginning.

## 2.1 Vision & Multimodal Models

These models are used for image understanding — extracting attributes like shape, color, lens type, and brand cues from uploaded images.

| Model | Provider | Capability | Tier |
|---|---|---|---|
| GPT-4o | OpenAI | Best-in-class vision, handles noisy real-world photos, returns structured JSON reliably | Paid |
| GPT-4o mini | OpenAI | Faster and cheaper than GPT-4o, slightly lower accuracy on complex images | Paid (Low Cost) |
| Claude 3.5 Sonnet | Anthropic | Excellent vision understanding, strong at structured attribute extraction | Paid |
| LLaVA 1.6 (34B) | Ollama / Hugging Face | Open-source multimodal model, runs locally, no API cost | Free (Self-hosted) |
| MiniCPM-V | Hugging Face | Lightweight multimodal, suitable for CPU-only environments | Free (Self-hosted) |
| CLIP (ViT-L/14) | OpenAI / HuggingFace | Embedding-only model, does not generate text; use for visual similarity vectors | Free |

**Recommended Pairing:**
- **Paid:** GPT-4o for attribute extraction + CLIP for embedding generation
- **Free:** LLaVA 1.6 for attribute extraction + CLIP for embedding generation

## 2.2 Language & Reasoning Models

These models handle intent extraction, query decomposition, style DNA synthesis, and conversational memory resolution.

| Model | Provider | Capability | Tier |
|---|---|---|---|
| GPT-4o | OpenAI | Best intent parsing, reliable JSON output, strong reasoning over web evidence | Paid |
| GPT-4o mini | OpenAI | 90% of GPT-4o quality at ~10% of the cost for simpler NL tasks | Paid (Low Cost) |
| Claude 3.5 Haiku | Anthropic | Fast, cheap, excellent for structured extraction tasks | Paid (Low Cost) |
| Claude 3.5 Sonnet | Anthropic | Strong at multi-step reasoning, style synthesis from evidence | Paid |
| Gemini 1.5 Flash | Google | Very fast, good at structured output, generous free tier | Free Tier Available |
| Mistral 7B Instruct | Ollama / HuggingFace | Open-source, strong intent parsing, runs locally | Free (Self-hosted) |
| Llama 3.1 8B Instruct | Meta / Ollama | Good for simpler decomposition tasks, no API cost | Free (Self-hosted) |

**Recommended Pairing:**
- **Paid:** GPT-4o for complex multi-step reasoning (Style DNA, query decomposition) + GPT-4o mini for simpler tasks (intent schema, normalization)
- **Free:** Gemini 1.5 Flash (free tier) for NL tasks + Mistral 7B locally for decomposition

## 2.3 Embedding Models

These models convert product text and query text into vectors for semantic similarity search.

| Model | Provider | Dimensions | Tier |
|---|---|---|---|
| text-embedding-3-small | OpenAI | 1536 | Paid (very low cost) |
| text-embedding-3-large | OpenAI | 3072 | Paid |
| embed-english-v3.0 | Cohere | 1024 | Paid (free tier available) |
| all-MiniLM-L6-v2 | HuggingFace (sentence-transformers) | 384 | Free |
| all-mpnet-base-v2 | HuggingFace (sentence-transformers) | 768 | Free |
| BAAI/bge-large-en-v1.5 | HuggingFace | 1024 | Free |

**Recommended Pairing:**
- **Paid:** text-embedding-3-small (low cost, high quality)
- **Free:** BAAI/bge-large-en-v1.5 (best free option, strong semantic understanding)

## 2.4 Object Detection Models

These models detect and locate eyewear within uploaded images so the pipeline can crop to the relevant product before passing to the vision model.

| Model | Provider | Capability | Tier |
|---|---|---|---|
| YOLOv8n | Ultralytics | Fastest, lightest, good for real-time detection | Free |
| YOLOv8m | Ultralytics | Better accuracy at moderate speed | Free |
| YOLOv9 | Ultralytics | State-of-the-art detection, higher accuracy | Free |
| Grounding DINO | HuggingFace | Open-vocabulary detection — can detect "sunglasses" by text prompt | Free |
| Roboflow API | Roboflow | Hosted detection with pre-trained eyewear models | Free Tier Available |

**Recommended:** YOLOv8n for speed during demo + Grounding DINO as fallback for text-prompted detection when standard YOLO classes don't cover eyewear accurately.

## 2.5 Web Search APIs

Used in the NL pipeline to research celebrity eyewear, movie styles, and event fashion.

| Service | Capability | Tier |
|---|---|---|
| Tavily Search API | AI-optimized search, returns clean summaries, ideal for LLM pipelines | Paid (free trial available) |
| SerpAPI | Google search results in structured JSON | Paid |
| Brave Search API | Privacy-focused, generous free tier (2,000 calls/month) | Free Tier |
| DuckDuckGo Search (ddg4py) | Unofficial Python wrapper, no API key needed | Free (unofficial) |
| Google Custom Search API | 100 free queries/day | Free Tier |

**Recommended:**
- **Paid:** Tavily (best quality for LLM consumption)
- **Free:** Brave Search API free tier (2,000 free calls is sufficient for a hackathon demo)

## 2.6 Vector Store / Database

Used to store and search product embeddings.

| Technology | Type | Tier |
|---|---|---|
| ChromaDB | In-memory / persistent, Python-native | Free |
| Qdrant | High-performance vector DB, Docker deployable | Free (self-hosted) |
| Pinecone | Managed cloud vector DB | Paid (free tier available) |
| Weaviate | Open-source, Docker deployable | Free (self-hosted) |
| FAISS | Meta's in-memory library, no server needed | Free |

**Recommended:** ChromaDB for simplicity in an 8-hour hackathon (zero configuration, Python-native). FAISS as alternative if ChromaDB has any dependency issues.

## 2.7 Phase-Wise Model Recommendation Summary

### Free Tier Stack (Zero API Cost)

| Layer | Model / Tool |
|---|---|
| Vision Attribute Extraction | LLaVA 1.6 via Ollama (local) |
| Object Detection | YOLOv8n (free) |
| Embeddings | BAAI/bge-large-en-v1.5 (HuggingFace) |
| NL Intent Extraction | Mistral 7B Instruct via Ollama (local) |
| NL Reasoning / Style DNA | Gemini 1.5 Flash (free tier — 15 RPM) |
| Web Search | Brave Search API free tier |
| Vector Store | ChromaDB (free) |
| Background Removal | rembg (free, local) |

**Tradeoff:** Slower inference (local models), lower accuracy on ambiguous images, requires a machine with at least 16GB RAM for local model serving.

### Paid Tier Stack (Recommended for Best Score)

| Layer | Model / Tool | Estimated Cost for Demo |
|---|---|---|
| Vision Attribute Extraction | GPT-4o | ~$0.01–0.05 per image |
| Object Detection | YOLOv8n (free) | Free |
| Embeddings | text-embedding-3-small | ~$0.0001 per product |
| NL Intent Extraction | GPT-4o mini | ~$0.001 per query |
| NL Reasoning / Style DNA | GPT-4o | ~$0.02–0.05 per query |
| Web Search | Tavily (trial) | Free trial available |
| Vector Store | ChromaDB | Free |
| Background Removal | rembg | Free |

**Estimated total cost for 8-hour hackathon demo:** Under $5 USD.

### Hybrid Stack (Recommended if Budget is Limited)

Use paid models only where accuracy is most visible to judges — vision extraction and style DNA — and free models for simpler tasks.

| Layer | Model |
|---|---|
| Vision Attribute Extraction | GPT-4o (paid — high visibility task) |
| Object Detection | YOLOv8n (free) |
| Embeddings | BAAI/bge-large-en-v1.5 (free) |
| NL Intent Extraction | Gemini 1.5 Flash (free tier) |
| NL Reasoning / Style DNA | GPT-4o mini (paid — low cost) |
| Web Search | Brave Search API (free tier) |
| Vector Store | ChromaDB (free) |

---

# 3. Technology Stack

## Data & Services Layer (Zone 1 — New in V4)

| Component | Technology | Purpose |
|---|---|---|
| Product Catalog DB | JSON flat-file (hackathon) → PostgreSQL (production) | Products, categories, attributes |
| Vector Database | ChromaDB | Embeddings generation & semantic search |
| Knowledge Graph | In-memory dict (hackathon) → Neo4j (production) | Brand, style, similarity relationships |
| Cache | Redis (Docker) | Session store, response caching |
| Search Index | Elasticsearch (Docker, optional) | Keyword search fallback |
| File Storage | Local `/data/` directory (hackathon) → S3 (production) | Images, documents |
| Session Store | Redis | Session DB across requests |
| User/Analytics DB | In-memory dict | Events, interactions for observability |
| **Data Services API Gateway** | FastAPI middleware | Unified access layer, auth, rate limiting, request validation, response standardization, caching layer |

## Backend Services (Zone 2 — MCP Server)

| Layer | Technology | Purpose |
|---|---|---|
| MCP Server Framework | Python + FastAPI | Async HTTP server, SSE streaming endpoint, OpenAPI documentation |
| Orchestrator | Custom Python class | Sequences tool calls, manages pipeline flow, emits stream events |
| Session Store | Redis (or in-memory dict) | Conversational memory, session state across turns |
| Background Removal | rembg (Python library) | Removes image backgrounds before attribute extraction |
| Object Detection | YOLOv8n (Ultralytics) | Detects and crops eyewear regions from uploaded images |

## Tools Layer (Zone 3)

| Tool | Technology | Purpose |
|---|---|---|
| Image Intelligence Tool | GPT-4o vision / LLaVA + rembg + YOLOv8 | Full image preprocessing → attribute extraction → StyleDNA |
| NL Understanding Tool | GPT-4o / Gemini + Tavily/Brave Search | Intent extraction + web research + evidence validation + StyleDNA |
| Catalog Intelligence Tool | ChromaDB + sentence-transformers | Product enrichment, style taxonomy, vectorization & indexing |
| Search & Retrieval Tool | ChromaDB + Elasticsearch | Hybrid search (vector + keyword), filtering, metadata search |
| Ranking & Scoring Tool | Custom Python scoring | Hybrid ranking formula, confidence check, explainability |
| Recommendation Tool | Catalog lookup | Budget / premium / trending alternatives |
| PDP / Cart / Checkout Tool | Mock data + session state | Product detail page navigation, cart management |

## Infrastructure

| Component | Choice | Reason |
|---|---|---|
| API Gateway | FastAPI middleware | Unified access, validation, rate limiting |
| Containerization | Docker Compose | Single command to start entire stack for demo |
| Catalog Storage | JSON flat-file | No database setup time required during hackathon |
| Cache | Redis (Docker image) | Session persistence, response caching |
| Environment Config | python-dotenv | API keys never hardcoded, easy to swap stacks |

---

# 4. Repository Structure

```
vision-to-cart/
│
├── data_services/                         # Zone 1 — Data & Services Layer (NEW in V4)
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
│   ├── confidence_governance.py           # Simplified: single 0.5 threshold (full routing = post-hackathon)
│   ├── error_recovery.py                  # ✅ MANDATORY: Retry × 2 + fallback tool + graceful response
│   └── observability.py                   # Basic: console logs + /metrics JSON endpoint (~15 lines)
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
│   ├── test_images/                       # 5+ test images for 3 demo scenarios
│   └── test_queries.txt                   # 5+ NL queries with expected outputs
│
├── scripts/
│   ├── ingest_catalog.py                  # One-time: embed + load catalog into ChromaDB + Redis
│   └── demo_test.py                       # Automated API calls for all 3 demo scenarios
│
├── docker-compose.yml                     # Starts: FastAPI + Redis + Elasticsearch (optional)
├── .env.example                           # All env vars documented with free-tier alternatives
└── README.md                              # Setup, run instructions, planned post-hackathon extensions
```

> **Note:** `mcp_client/` (React frontend) is **removed from 8-hour scope**. Demo runs via `scripts/demo_test.py` or Postman hitting the `/mcp/stream` SSE endpoint directly.

---

# 5. Core Architecture — V4

See `HLD_diagram_hackathon_v4.png` for the approved architecture diagram.

## 5.1 The Three Zones

The entire system is divided into three physical zones. Nothing crosses zone boundaries except through defined contracts.

**Zone 1 — Data & Services Layer**
The primary data backbone (new in V4). Contains: Product Catalog DB, Vector Database (ChromaDB), Knowledge Graph, Cache (Redis), Search Index (Elasticsearch), File Storage, Session Store, and User/Analytics DB. All tools access data exclusively through the Data Services API Gateway — a unified access layer that handles auth, rate limiting, request validation, response standardisation, and caching. No tool queries a data store directly.

**Zone 2 — MCP Server (Orchestration Layer)**
The orchestration brain. Contains the MCP Orchestrator (Intent Router, Context Manager, Plan Executor, Response Composer, Tool Router, Workflow Manager, Memory Manager). Also contains the cross-cutting layers applied across orchestrator and tools: Simplified Confidence Governance, Error Recovery (mandatory), Security (basic), and Observability (basic). The server never exposes AI model calls externally.

**Zone 3 — Tools (Execution Layer)**
Six independently callable tools, each with a typed input and output. No tool calls another tool. The orchestrator is the only entity that calls tools via the Tool Router.

## 5.2 Unified Product Intelligence Core

The key V3 architectural insight is that the Image Pipeline and the NL Pipeline are not separate systems — they are two different routes to the same destination: a **Style DNA object** that is then fed into a single **Unified Product Intelligence Core**.

```
Image Upload ──► Image Pipeline ──► Style DNA
                                         │
                                         ▼
NL Query ─────► NL Pipeline ────►  Unified Product Intelligence Core
                                         │
                                         ▼
                                    Hybrid Retrieval
                                         │
                                         ▼
                                      Re-ranking
                                         │
                                         ▼
                                   Explainability
                                         │
                                         ▼
                                   Recommendations
                                         │
                                         ▼
                                  Feedback Learning
```

This design means all ranking, confidence, and recommendation logic is written once and shared by both pipelines.

## 5.3 Data Models (Described, Not Code)

### MCPRequest
Sent from client to server. Contains: session ID, input type (image or text), the image encoded as base64 if applicable, and the text query if applicable.

### MCPStreamEvent
Sent from server to client via SSE. Contains: event type (step_start, step_complete, heartbeat, result_ready, error), the human-readable step label, and optional payload data for result events.

### StyleDNA
The universal intermediate object used throughout both pipelines. Contains: shape, frame color, lens color, frame material, gender, style tags, brand hint, price range preference, confidence score, and source (image / nl / web). Both pipelines produce a StyleDNA and both pass it to the unified intelligence core.

### ProductMatch
The final result object returned to the client. Contains: product ID, name, image URL, PDP URL, confidence percentage, confidence tier (High / Medium / Low), human-readable match reason, detailed score breakdown, and recommendation tier (exact / budget / premium / trending).

## 5.4 Tool Contracts

Each tool is defined by three things: its single responsibility, its input type, and its output type. The orchestrator calls each tool in sequence and passes outputs forward.

| Tool | Responsibility | Input | Output |
|---|---|---|---|
| ImageIntelligenceTool | Preprocessing → YOLOv8 detection → GPT-4o attribute extraction | Image (base64) | StyleDNA |
| NLUnderstandingTool | Intent extraction + web search (Tavily/Brave) + evidence validation + DNA synthesis | Query text + session context | StyleDNA + evidence list |
| CatalogIntelligenceTool | Attribute enrichment, style classification, CLIP embeddings, metadata & keyword indexing | Raw catalog products | Enriched products + vectors in ChromaDB |
| SearchRetrievalTool | Hybrid search (vector + keyword), filtering by assets/brand/price, relevance ranking, Top-N | StyleDNA + filters | Candidate product list |
| RankingScoringTool | 5-component hybrid score, tie-ranking via cross-encoder, confidence check, explainability | Candidates + StyleDNA | Ranked ProductMatch list |
| RecommendationTool | Budget / premium / trending alternatives from catalog | Top match + StyleDNA | Recommendation set (3 tiers) |
| PDPCartCheckoutTool | Mock PDP lookup, Add-to-Cart, cart session management | Product ID + session ID | PDP data / cart state |

---

# 6. Phase 0 — Setup & Scaffolding (Hour 0–1)

## Goals

- Repository initialized with the complete folder structure
- Environment variables configured and all dependencies installable in one command
- Mock catalog created with 30+ products
- Product embeddings pre-computed and stored in ChromaDB
- Stub versions of all tools returning placeholder data (so the full pipeline runs end-to-end before any real AI logic is added)

## 6.1 What to Build First

The most important principle of the 8-hour build is: **get the full pipeline running with stubs before adding intelligence.** This means the client can connect, send a request, receive SSE events, and display a result card — all using hardcoded placeholder data — within the first hour. Intelligence is layered in later.

## 6.2 Catalog Design

The mock catalog is the foundation of the entire system. Its quality directly determines how well the hybrid ranking performs. Build it with diversity across all searchable dimensions:

**Shape variety:** At least 3 products per shape (aviator, round, rectangle, cat-eye, oval, sport, square). A minimum of 7 distinct shapes total.

**Color variety:** Cover gold, silver, black, brown, clear frames. Cover green, brown, gray, blue, clear, mirror lenses.

**Material variety:** Metal, acetate, titanium, wooden frames.

**Style tag variety:** Luxury, casual, sporty, classic, trendy — each represented by at least 4 products.

**Price range variety:** Budget (under ₹2,000), mid (₹2,000–₹8,000), premium (above ₹8,000) — roughly one-third each.

Each product record must contain all searchable fields: product_id, name, brand, shape, frame_color, lens_color, frame_material, gender, style_tags (list), price, popularity_score (1–100), pdp_url, and image_url.

## 6.3 Embedding Ingestion

During startup, the server builds a text representation of each product from its attributes and sends it to the embedding model. The resulting vector is stored in ChromaDB alongside the product metadata. This process should complete in under 2 minutes for 30 products and only runs once — subsequent starts read from a cache.

The text representation must include all searchable attributes written in natural language so that the embedding captures semantic meaning, not just keywords.

## 6.4 Environment Configuration

The `.env.example` file must document every variable the system depends on, with clear comments about which are required vs optional and which free-tier alternatives exist. No API key should ever appear in source code.

---

# 7. Phase 1 — Data & Services Layer Bootstrap (Hour 0–1, parallel with Phase 0)

## Goals

- Redis running via Docker
- `data_services/api_gateway.py` scaffolded with stub responses for all data operations
- `catalog.json` created with 30+ products and all required fields
- `scripts/ingest_catalog.py` embeds all products into ChromaDB
- Elasticsearch Docker container running (optional — used as keyword search fallback)
- All data stores reachable from `mcp_server/` via the API Gateway

## 7.1 Data Services API Gateway

The API Gateway is a thin FastAPI router (`data_services/api_gateway.py`) that sits between the MCP tools and the data stores. Every tool that needs data calls the gateway — never a data store directly. The gateway handles:

**Unified access:** One interface regardless of which store backs the data (ChromaDB, Redis, Elasticsearch, or JSON file).

**Request validation:** Reject malformed queries before they reach a data store.

**Rate limiting:** Simple per-session request counter to prevent runaway API calls.

**Response standardisation:** All data responses follow the same envelope: `{status, data, error, latency_ms}`.

**Caching layer:** Redis-backed cache for repeated identical queries within a session. A StyleDNA search repeated with the same parameters in a follow-up query hits the cache, not ChromaDB.

## 7.2 Docker Compose Setup

The `docker-compose.yml` must start the full stack with one command: `docker compose up`. Services:

- `mcp_server` — FastAPI app (port 8000)
- `redis` — Redis 7 Alpine (port 6379)
- `elasticsearch` — Elasticsearch 8 (port 9200, optional — can comment out for hackathon if time is tight)

ChromaDB runs in-process (no Docker needed) with a persistent directory mount.

---

# 8. Phase 2 — MCP Server & Tool Contracts (Hour 1–2)

## Goals

- FastAPI server running at localhost with the `/mcp/stream` SSE endpoint
- All tool interfaces defined with typed inputs and outputs
- Orchestrator pipeline sequencer operational (with stub tools)
- Context Manager storing and retrieving session state
- Security layer (input validation + session isolation) applied at the endpoint level
- Error Recovery layer (retry + fallback) wrapping every tool call

## 8.1 The SSE Endpoint

The `/mcp/stream` endpoint accepts a POST request with an `MCPRequest` body and returns a streaming response using the `text/event-stream` content type. Each event is a JSON-serialized `MCPStreamEvent`. The connection stays open until the orchestrator emits a `result_ready` or `error` event.

The endpoint must validate the incoming request before passing it to the orchestrator: check that session_id is present and alphanumeric, that input_type is one of the allowed values, that the image payload (if present) is valid base64 and under the size limit, and that the text query (if present) is not empty and passes basic injection screening.

## 8.2 Orchestrator Design

The Orchestrator is the most important module in the system. It works as follows:

When a request arrives, the Orchestrator first resolves it through the Context Manager — checking if this is a follow-up query that should inherit context from a previous turn in the same session. It then classifies the request as IMAGE_SEARCH or NL_SEARCH based on input type. It builds an ordered list of sub-tasks specific to the pipeline. For each sub-task, it emits a `step_start` event, calls the appropriate tool via the Tool Router, emits a `step_complete` event with the tool output, and passes the output forward to the next sub-task. After all sub-tasks complete, it emits a `result_ready` event with the final ranked product list. Throughout this process, it emits `heartbeat` events every 3 seconds if a step is taking unusually long.

The Orchestrator never calls tools directly — it always goes through the Tool Router. This separation allows individual tools to be replaced without touching the orchestrator.

## 8.3 Tool Router Design

The Tool Router is a simple dispatcher. It maintains a registry of all tools keyed by their name. When the orchestrator calls `route("image_tool", input)`, the router finds the registered ImageTool, calls it with the input, and returns the output. The router is also the point where the Error Recovery layer is applied — it wraps every tool call in a retry + fallback chain.

## 8.4 Context Manager Design

The Context Manager maintains a dictionary of session states keyed by session_id. Each session state stores: the last resolved intent schema, the last generated Style DNA, the filters last applied, the list of product IDs shown to the user, and the timestamp of the last interaction. When a new request arrives with an existing session_id, the Context Manager checks whether the query contains refinement signals ("cheaper," "similar," "different color," "same brand") and if so, merges the new request with the existing session context before passing it to the orchestrator.

## 8.5 Error Recovery Design

Every tool call is wrapped in a three-layer recovery strategy:

**Layer 1 — Retry:** If a tool fails due to a transient error (network timeout, API rate limit), retry up to 2 times with exponential backoff (wait 1 second, then 3 seconds).

**Layer 2 — Fallback Tool:** If retries are exhausted, activate the fallback for that specific tool. For example, if the primary web search tool (Tavily) fails, fall back to the secondary search tool (Brave Search). If the primary vision model fails, fall back to the smaller/faster vision model.

**Layer 3 — Graceful Response:** If the fallback also fails, return a partial result rather than an error. For example, if all web search fails during an NL query, fall back to a direct style-tag search against the catalog using whatever intent was extracted from the query text alone. The user always sees some result.

---

# 9. Phase 3 — Catalog Intelligence Service (Hour 2–3)

## Goals

- Products enriched with style taxonomy, trend tags, and similarity graph
- Normalization dictionary fully populated
- Style DNA object defined and used by both pipelines
- Feedback store initialized (even if empty at start)

This phase replaces the simpler "Product Intelligence Layer" from V2 with a richer Catalog Intelligence Service that treats the catalog as a living knowledge graph, not just a searchable table.

## 9.1 Product Enrichment

Beyond the base catalog attributes, each product must be enriched with additional computed fields before being ingested into the vector store:

**Style Taxonomy Tag:** A single high-level classification assigned from a fixed taxonomy: `classic-luxury`, `casual-everyday`, `sport-performance`, `fashion-forward`, `minimalist-clean`. This tag is used by the recommendation engine to find alternatives within the same or adjacent taxonomy class.

**Trend Score:** A numeric value (0–100) indicating how "current" or "on-trend" the product is. For the mock catalog, this can be assigned manually based on general knowledge of current eyewear trends (oversized frames, tinted lenses, and thin metal frames are trending as of 2024–2025).

**Similar Product Graph:** *(Document only — post-hackathon extension)* Each product would store a list of 3–5 similar product IDs for fast alternative lookups. Skip manual pre-computation during the 8-hour build. The recommendation engine will use embedding similarity at query time instead. Document this as a planned optimization in the README.

**Gender Affinity:** Some products are nominally unisex but have a stronger association with one gender based on style cues. Enrich each product with a `gender_affinity` field that goes beyond the binary male/female/unisex label.

## 9.2 Attribute Normalization Dictionary

The normalization dictionary is a critical component that bridges the gap between the language used by vision models and the language used in the product catalog. Without it, a vision model that returns "golden metal frame" will not match a catalog product labeled "gold frame."

The dictionary must cover at minimum:

**Shape normalization:** Maps informal descriptors (aviators, teardrop, butterfly, wrap-around, sporty, oversized) to the standard catalog shape taxonomy.

**Color normalization:** Maps descriptive color names (golden, silvery, tortoiseshell, rose gold, dark black, transparent, brownish) to the standard catalog color values.

**Material normalization:** Maps informal descriptions (metallic, plastic, shell, wooden, tortoise) to standard material categories (metal, acetate, wooden, titanium).

**Style normalization:** Maps informal style language (flashy, understated, athletic, fashion-forward) to the standard style_tag vocabulary.

Normalization is applied to vision model output BEFORE the normalized attributes are used to build the Style DNA. This single step has the largest impact on embedding search quality.

## 9.3 Style DNA as Universal Intermediate

The Style DNA object is the single most important data structure in the system. Both the Image Pipeline and the NL Pipeline produce one StyleDNA object as their output, and both pass it to the same Unified Product Intelligence Core for retrieval and ranking.

A StyleDNA captures: shape, frame color, lens color, frame material, gender, style tags, brand hint (optional), price range preference (optional), confidence score, and source field indicating whether it came from an image, NL extraction, or web evidence synthesis.

The StyleDNA also exposes a `to_search_text()` method that converts its attributes into a natural-language sentence suitable for generating a search embedding. This sentence is what gets embedded and compared against the pre-computed product embeddings in ChromaDB.

## 9.4 Feedback Store — Document Only

> **Review Note:** The Feedback Learning Loop has no demo-visible impact in a single hackathon session. Implementing it consumes hours without adding judge-visible value. Skip implementation during the 8-hour build.

The Feedback Store design is fully specified here for post-hackathon implementation. It would record: product_id, event_type (viewed / clicked / added_to_cart), session_id, and timestamp. The RankingTool would read from it to boost popularity weights for frequently clicked or carted products.

**For the hackathon:** The RankingTool uses the static `popularity_score` field from `catalog.json`. Document in the README that real-time feedback integration is a planned V4 extension.

---

# 10. Phase 4 — Image Discovery Pipeline (Hour 3–5)

## Goals

- Real image uploads handled end-to-end with real vision model calls
- Object detection correctly crops eyewear from real-world photos
- Attributes extracted, normalized, and converted to Style DNA
- Hybrid ranking formula computing all five components
- Confidence Governance routing correctly based on score
- Explainability output showing why each product was matched
- Fallback search triggering reliably on low-confidence results

## 13.1 Vision Preprocessing (ImageTool — Step 1)

**Purpose:** Convert a raw uploaded image into a clean, cropped product view that maximizes attribute extraction accuracy.

**How it works:**

The uploaded image arrives as a base64-encoded string. The ImageTool first decodes it to raw bytes and loads it as a PIL Image object. It then resizes the image to a standard processing resolution (640×640 pixels). Background removal is applied using the rembg library, which uses a U2-Net neural network to isolate foreground objects from backgrounds — this dramatically improves attribute extraction for real-world photos of glasses worn by people or lying on surfaces.

The cleaned image is passed to the object detection model. YOLOv8 runs inference and returns bounding boxes for all detected objects. The tool searches for bounding boxes corresponding to eyewear classes (sunglasses, glasses). If a confident detection is found, the image is cropped to that bounding box with a small padding margin. If no eyewear is detected, the full background-removed image is passed forward with a note in the pipeline metadata indicating that detection was skipped.

**Failure handling:** If background removal fails (some images confuse the model), proceed without it. If object detection produces no results, proceed with the full image and add the instruction "Focus on any eyewear present" to the vision model prompt.

## 13.2 Attribute Extraction (ImageTool — Step 2)

**Purpose:** Convert the processed image into a structured attribute dictionary that can be normalized and assembled into a StyleDNA.

**How it works:**

The cropped, cleaned image is encoded back to base64 and sent to the vision model (GPT-4o or LLaVA depending on tier). The prompt instructs the model to return a JSON object with exactly the following fields: shape, frame_color, lens_color, frame_material, gender, style_tags (as a list), and brand_hint (or null if undetectable). The prompt also instructs the model to use simple standard vocabulary for each field rather than elaborate descriptions.

The model response is parsed as JSON. If parsing fails (the model returned prose instead of JSON), the extraction is retried once with a stricter prompt that reinforces the JSON-only output requirement. If the retry also fails, the available partial attributes are used and missing fields are left as null.

**Normalization:** Every extracted attribute is passed through the normalization dictionary before assembly into a StyleDNA. "golden" becomes "gold", "roundish" becomes "round", etc.

## 13.3 Hybrid Ranking (RankingTool)

**Purpose:** Score the candidate products from the vector store using five components to produce a final, human-interpretable ranking.

**How it works:**

The StyleDNA's search text is embedded using the same model used at catalog ingestion time. The resulting vector is queried against ChromaDB to retrieve the top 20 candidates by cosine similarity. Each candidate is then scored using the five-component formula:

**Embedding Similarity (40%):** The raw cosine similarity from the vector search, normalized to 0–1.

**Shape Match (20%):** Exact match scores 1.0. Shapes in the same family (e.g., aviator and teardrop are both elongated) score 0.5. No relationship scores 0.

**Brand Match (15%):** If the StyleDNA contains a brand_hint and the candidate matches, score 1.0. Otherwise 0. If no brand_hint exists, this component is redistributed proportionally to the other components.

**Lens Color Match (15%):** Exact match scores 1.0. Similar color families (e.g., brown and amber) score 0.5. No match scores 0.

**Metadata Match (10%):** Computed as the Jaccard similarity between the StyleDNA style_tags and the product style_tags, plus a bonus for material match and gender match.

The final five-component score is multiplied by the product's popularity weight from the Feedback Store. The top 4 results are returned as ProductMatch objects.

## 12.4 Confidence Governance — Simplified Implementation

**Purpose:** Surface low-confidence results gracefully without building a full routing tree.

> **Review Note:** The full three-tier routing (high/medium/low thresholds with supplementary search triggers) is architecturally correct but takes real implementation time and is unlikely to be noticed by judges in a 15-minute demo unless explicitly called out. The simplified version below ships in 20 minutes, survives live demo conditions, and is visually identical from the judge's perspective.

**How it works:**

After ranking, check the top result's confidence score against a single threshold:

- **If confidence ≥ 0.5:** Return the ranked results as-is. The UI displays confidence badges normally.
- **If confidence < 0.5:** Return the results but display the message: *"Here are some alternatives we think you might like"* instead of presenting them as exact matches. No supplementary search is triggered.

This single check handles the visible demo behaviour — judges see the system respond intelligently to uncertainty — without the engineering overhead of building the full routing tree.

**Post-Hackathon Extension:** Implement the full three-tier routing (90–100% / 70–89% / below 70%) with supplementary attribute-based search triggers as described in the original V3 spec. This is a straightforward extension once the core pipeline is working.

## 12.5 Explainability Engine

**Purpose:** Show the user (and the judges) exactly why each product was matched.

**How it works:**

For each ProductMatch, the ranking tool constructs a human-readable explanation by comparing the StyleDNA attributes against the product attributes. Each matched attribute is listed with a checkmark. The similarity score is included. The explanation is stored in the `match_reason` field of the ProductMatch and displayed directly in the UI on the product card.

Example output: "Matched because: ✓ Aviator shape ✓ Green lens ✓ Thin metal frame — Similarity Score: 91%"

## 12.6 Fallback Search Chain

**Purpose:** Ensure the user always receives a useful result, even when the primary search fails.

**How it works:**

The fallback chain is executed in order, stopping as soon as a non-empty result is found:

**Strategy 1 — Attribute Filter Search:** Query the catalog directly for products where `shape` equals the extracted shape, bypassing the vector store entirely. Returns all exact shape matches.

**Strategy 2 — Style Tag Search:** Query for products containing any of the StyleDNA's style tags. Ranks by number of tag overlaps.

**Strategy 3 — Popularity Fallback:** Return the 3 products with the highest popularity scores from the Feedback Store (or the 3 manually designated as "best sellers" in the catalog if the Feedback Store is empty).

---

# 11. Phase 5 — Natural Language Discovery Pipeline (Hour 5–6.5)

## Goals

- Any natural language query (including celebrity/movie references and vague style descriptions) resolved to relevant products
- Multi-source web evidence gathered and validated before Style DNA is synthesized
- Conversational follow-up queries correctly resolved using session memory
- NL re-ranking formula using all four components

## 13.1 Context Resolution

**Purpose:** Determine whether the incoming query is a fresh search or a refinement of the previous session.

**How it works:**

The Context Manager inspects the query for refinement signals: words and phrases like "cheaper," "more expensive," "similar," "different color," "same brand," "show me more," "budget option," "premium version." If any are present and the session has a stored intent and StyleDNA, the new query is merged with the previous context. The merged query carries forward the previous style profile and applies the new constraint as an additional filter. This allows a natural conversational flow: first query establishes the profile, subsequent queries refine it.

## 13.2 Intent Schema Extraction

**Purpose:** Convert any natural language input into a structured, machine-queryable intent object.

**How it works:**

The query is sent to the language model with a carefully engineered prompt that instructs it to identify and extract: actor or celebrity name, movie or show name, event name (Cannes, Oscars, etc.), product type (sunglasses, eyeglasses, frames), style descriptors (minimalist, luxury, sporty, etc.), price preference, and gender. The model returns a JSON object.

This extraction is robust to vague inputs. For "Something like what celebs wear at Cannes," it extracts: event="Cannes", style_descriptors=["luxury", "fashion-forward"], product_type="sunglasses", actor=null. For "Minimalist gold frame glasses," it extracts directly: style_descriptors=["minimalist"], frame_color="gold", product_type="glasses" — and does not trigger a web search since no external reference is needed.

The intent schema extraction step decides whether a web search is necessary: if actor, movie, or event fields are populated, web search is triggered. If only style descriptors and product attributes are present, the system can skip web search and go directly to catalog search.

## 13.3 Query Decomposition

**Purpose:** Break a single user query into multiple targeted search tasks that together provide sufficient evidence to characterize the product.

**How it works:**

Given an intent schema, the query decomposer generates 3–5 distinct search queries, each targeting a different angle of the same topic. For "Akshay Khanna in Dhurandhar":

- Query 1: "Akshay Khanna Dhurandhar movie sunglasses" (direct product reference)
- Query 2: "Akshay Khanna Dhurandhar character style eyewear" (style characterization)
- Query 3: "Dhurandhar movie promotional photos Akshay Khanna" (image-based reference)
- Query 4: "Akshay Khanna 2024–2025 eyewear style interviews" (recent style signals)

Multiple queries address the core problem that any single search query may miss the specific content needed.

## 12.4 Multi-Source Web Search

**Purpose:** Retrieve raw web evidence from multiple independent sources to reduce the risk of biased or inaccurate results.

**How it works:**

Each decomposed query is sent to the web search API. Results are collected from all queries, deduplicated by URL, and stored as a flat evidence list. Each evidence item contains: the source URL, the snippet/summary text, and a relevance score from the search API. The full evidence list is then passed to the Evidence Validation layer.

The system uses at least two search result pages per query when available, since the most relevant information is sometimes in the second result rather than the first.

## 12.5 Evidence Validation

**Purpose:** Filter out unreliable or irrelevant web search results before they contaminate the Style DNA synthesis.

**How it works:**

Each evidence item is scored on three criteria:

**Source Credibility:** Results from known entertainment news sites, IMDb, official brand sites, and major newspapers score higher than forum posts or low-authority blogs.

**Attribute Corroboration:** An attribute is only accepted if at least 2 independent sources mention it. A single source saying "black aviator frames" is insufficient. Two or more sources agreeing constitutes validated evidence.

**Recency:** For celebrity style searches, more recent articles are preferred over older ones to ensure the style reference matches the right time period.

Evidence items that fail validation are filtered out. If fewer than 2 valid items remain after filtering, the system triggers the retry strategy.

## 12.6 Style DNA Synthesis from Web Evidence

**Purpose:** Convert the validated web evidence into a StyleDNA object that can be passed to the Unified Product Intelligence Core.

**How it works:**

The validated evidence snippets are concatenated and sent to the language model with a prompt that instructs it to synthesize a StyleDNA JSON from the available information. The model identifies the most commonly mentioned attributes across the evidence, assigns a confidence score based on how consistent the evidence is (high confidence if all sources agree, lower if sources partially conflict), and returns the structured JSON.

The confidence score embedded in the web-sourced StyleDNA reflects evidence quality, not just attribute completeness. A StyleDNA with 3 well-corroborated attributes and confidence 80% is more valuable than one with 7 attributes and confidence 45%.

## 11.7 Search Filter Pre-pass

**Purpose:** Reduce the vector search space by applying hard filters before semantic similarity is computed.

**How it works:**

Before running embedding search, the system applies any hard constraints from the intent schema as metadata filters in ChromaDB. These filters include: price range (if a price preference was extracted), gender (if specified), and product type (sunglasses vs. eyeglasses). This pre-pass removes irrelevant products from the candidate pool and improves the quality of the remaining cosine similarity results.

## 11.8 NL Re-ranking Formula

The NL pipeline uses a modified ranking formula that incorporates web evidence quality:

**Catalog Similarity (40%):** Cosine similarity between the Style DNA embedding and the product embedding.

**Style DNA Confidence (25%):** The confidence score attached to the StyleDNA by the synthesis step. Products matched against high-confidence DNA rank higher.

**Product Popularity (20%):** Popularity score from the Feedback Store.

**Result Freshness (15%):** Products recently added to the catalog or with recent interaction signals in the Feedback Store score higher. For the hackathon mock catalog, this can be a manually assigned recency score.

## 11.9 Retry Strategy

If the NL pipeline's web search returns insufficient evidence after validation, the system executes the retry chain:

**Retry 1 — Actor-Only Search:** If actor + movie returns no evidence, try actor alone.
**Retry 2 — Style Descriptor Search:** If actor search also fails, use only the style descriptors from the intent schema to build a StyleDNA directly, bypassing web search entirely.
**Retry 3 — Trend Search:** Search for "trending [product_type] styles [current year]" to find popular products in the right category.
**Retry 4 — Popularity Fallback:** Return popular products in the requested product type.

The system never returns an empty result set. The user always sees products, even if they are not a perfect match.

---

# 12. Phase 6 — Streaming & Cross-Cutting Layers (Hour 6.5–7.5)

> **Note:** Frontend (React client) is out of scope for the 8-hour build. SSE streaming output is verified via `scripts/demo_test.py`. Sections 12.1 and 12.2 describe the server-side stream design; Sections 12.3–12.6 cover the cross-cutting layers.

## Goals

- SSE stream rendered progressively in the UI with step-by-step animation
- Product cards displaying all required information including confidence badges and match explanations
- Recommendation strip showing budget / premium / trending alternatives
- Observability layer capturing latency and error metrics
- Security layer enforced at the request boundary

## 13.1 SSE Stream Consumer

**Purpose:** Connect the React frontend to the FastAPI SSE endpoint and translate raw stream events into UI state updates.

**How it works:**

A custom React hook (`useSSEStream`) manages the SSE connection lifecycle. When a request is submitted, the hook opens an SSE connection to `/mcp/stream`, iterates over incoming event lines, parses the JSON payload of each event, and dispatches state updates to the component tree. `step_start` events add a pending item to the progress list. `step_complete` events mark that item as complete and animate the checkmark. `heartbeat` events trigger a subtle pulse animation on the most recent pending step to communicate that processing is ongoing. `result_ready` events populate the product grid and dismiss the progress overlay.

## 13.2 Progress Display

**Purpose:** Keep the user engaged during the 10–30 seconds of AI processing.

**How it works:**

The ProgressStream component renders a vertical list of steps. Completed steps show a green animated checkmark. The current in-progress step pulses with a loading spinner. Future steps are grayed out. Each step label is written in natural, friendly language: "🔍 Analyzing your image," "🕶️ Spotting the frame style," "🌐 Researching similar styles," "📦 Matching with catalog," "🏆 Ranking your results."

A skeleton loader replaces the product grid area while processing is ongoing. When results arrive, the skeleton fades out and the product cards fade in with a staggered animation.

## 13.3 Product Cards

**Purpose:** Present each matched product with all the information needed to evaluate the match and proceed to purchase.

**How it works:**

Each product card displays: the product image, product name and brand, price, a color-coded confidence badge (green for High, yellow for Medium, red for Low), the human-readable match explanation, and a "View Product" button that navigates to the mock PDP. The confidence badge tooltip shows the full score breakdown when hovered.

## 12.4 Recommendation Strip

**Purpose:** Present alternatives to the top match to help users discover related products and improve engagement.

**How it works:**

Below the main product grid, a horizontal scrollable strip shows four recommendation tiles: the exact match (highlighted), a budget alternative (same style, lower price), a premium upgrade (same style, higher quality), and a trending option (currently popular in the same category). Each tile is smaller than the main cards and includes a label indicating its recommendation tier.

## 12.5 Observability Layer — Minimal Implementation Only

> **Review Note:** A full observability dashboard will consume hours without adding judge-visible value beyond what a simple JSON endpoint already demonstrates. Do not build a dashboard during the 8-hour window.

**What to implement (20 minutes max):** A single `/metrics` GET endpoint that returns a JSON object showing the last request's per-tool timing breakdown and success/failure status. This is sufficient to mention during the demo as evidence of production-quality thinking.

```python
# observability.py — minimal implementation
_metrics = {}

def record(tool_name, duration_ms, success, error=None):
    _metrics[tool_name] = {"duration_ms": duration_ms, "success": success, "error": error}

def get_metrics():
    return _metrics
```

**Post-Hackathon Extension:** Replace the in-memory dict with a proper observability backend (OpenTelemetry, Prometheus, or Langfuse). Add dashboards, alerting, and per-session accuracy tracking as described in the full V3 spec.

## 12.6 Security — Inline Validation Only

> **Review Note:** A full security module (`security.py`) is post-hackathon scope. For the demo, inline the essential guards directly into the SSE endpoint. This takes 15 minutes and covers what judges can see.

**What to implement inline in `main.py`:**

- Reject `session_id` values that contain characters outside `[a-zA-Z0-9-]`
- Reject image payloads over 10MB
- Reject empty or missing `query` fields
- Wrap user text in explicit `<user_input>...</user_input>` delimiters before passing to any LLM prompt (basic injection protection)

That is sufficient for a hackathon submission. Document in the README that production deployment would add rate limiting, auth, and a dedicated security middleware layer.

---

# 13. Phase 7 — Testing & Demo (Hour 7.5–8)

## Goals

- All three demo scenario scripts run without errors end-to-end
- Every demo scenario produces the expected output (defined in `inputs/test_queries.txt`)
- Docker Compose starts the full stack with one command
- Demo video recorded cleanly and under 15 minutes
- Submission package assembled with all required components

## 13.0 The 3 Required Demo Scenarios

These three scenarios must be defined with expected outputs **before starting the build**. Write them into `inputs/test_queries.txt` and `scripts/demo_test.py` on Day 1.

| Scenario | Input | Expected Output |
|---|---|---|
| **Scenario 1 — Image Search** | Real-world photo of aviator sunglasses (person wearing them, busy background) | Top result: aviator shape, confidence ≥ 0.7, match explanation showing shape + lens color match |
| **Scenario 2 — NL Celebrity Search** | "Sunglasses worn by Akshay Khanna in Dhurandhar" | Web search triggered, StyleDNA synthesized from evidence, top result matches extracted style profile |
| **Scenario 3 — Conversational Refinement** | "Show me cheaper options" (same session as Scenario 2) | Price filter applied, web search skipped (context from Redis), budget-tier products returned |

Run all three via `python scripts/demo_test.py` — this prints pass/fail for each scenario automatically.

## 13.1 Pre-Demo Test Cases

Run every test case listed below before recording the demo video. Any failure must be resolved before recording.

### Image Pipeline Test Cases

| Test | Input Description | Expected Result |
|---|---|---|
| Clean catalog image | Direct copy of a catalog product photo | Confidence > 90%, exact or near-exact product match |
| Real-world photo with background | Phone photo of sunglasses on a table | Background removed, product detected, reasonable match |
| Person wearing glasses | Photo of a face with sunglasses | Glasses cropped from face, attributes extracted accurately |
| Partial visibility | Only half the frame visible | Graceful degradation, medium confidence, fallback triggered |
| Non-eyewear image | Photo of a bag or shoe | No eyewear detected, polite message, popular products shown |

### NL Pipeline Test Cases

| Test Query | Expected Behavior |
|---|---|
| "Sunglasses worn by Akshay Khanna in Dhurandhar" | Web search triggered → evidence validated → Style DNA → products |
| "Something like what celebs wear at Cannes" | Event-based search → luxury style DNA → premium products |
| "Minimalist gold frame glasses" | Direct attribute extraction, no web search, fast result |
| "Show me cheaper options" (after any search) | Session memory loads, price filter applied, budget tier results |
| "What about in black?" (after any search) | Session memory loads, color filter updated, same style in black |

### MCP Architecture Test Cases

- Confirm session_id persists across at least 3 turns in the same browser tab
- Confirm SSE stream shows at least 5 distinct step events before results appear
- Confirm fallback triggers when given a deliberately ambiguous query with no web results
- Confirm the `/metrics` endpoint returns accurate latency data

## 13.2 Demo Video Script

**Duration:** Maximum 15 minutes. Aim for 12 minutes with 3 minutes buffer.

**Section 1 — Architecture Overview (0:00–1:30)**
Open with the Architecture Diagram on screen. Walk through the three zones (client, server, tools) in 60 seconds. Call out Error Recovery as the mandatory V3 addition — briefly show a fallback triggering. Mention the other V3 layers (Confidence Governance, Feedback Loop, Observability, Security) as designed and documented for post-hackathon implementation. Keep this brief — judges want to see the system running.

**Section 2 — Image Search Flow (1:30–5:00)**
Send a real-world photo of sunglasses (not a catalog image) via `demo_test.py` or Postman. Show the SSE stream output step by step in the terminal. Show the final JSON result with top 4 products, confidence scores, and match explanations. Navigate to the mock PDP endpoint and show the JSON response.

**Section 3 — NL Search Flow (5:00–9:00)**
Send: "Sunglasses worn by Akshay Khanna in Dhurandhar" via demo script. Show SSE stream steps in terminal — highlight the web search steps (indicate sources being searched). Show the StyleDNA JSON object synthesized from evidence. Show matched products with confidence scores in the final JSON.

**Section 4 — Conversational Refinement (9:00–11:00)**
Send: "Show me cheaper options" with the same session_id. Show that SSE stream skips web search steps (context is cached in Redis) and goes directly to re-ranking with a price filter applied. Show budget-tier products in the final JSON.

**Section 5 — Architecture Callout (11:00–12:00)**
Briefly show the `/metrics` JSON endpoint in the browser — one line explaining it tracks per-tool latency and error recovery triggers. Then call out the V3 layers that are designed but scoped for post-hackathon: feedback loop, full observability dashboard, three-tier confidence routing. This positions the team as thinking beyond the demo, not just building a toy.

**Section 6 — Closing (12:00–13:00)**
State the architecture decisions you are most proud of and one thing you would improve with more time. Keep it confident and concise.

---


# 14. Remaining Risks & Mitigations

These are risks that remain even after all V3 improvements. Every team member must be aware of them before the build starts.

## Risk 1 — Real Magrabi Catalog Unavailable

**Problem:** The actual Magrabi product database is not accessible. The mock catalog must stand in for it.

**Impact:** Product mapping accuracy is limited by the mock catalog's diversity. If the catalog lacks a product in the right shape/color combination, no ranking algorithm can match it.

**Mitigation:** Build the mock catalog with maximum diversity (see Section 6.2). Cover every major shape, color, and material combination. Assign at least one high-popularity product to each combination so fallback searches always find something reasonable. Document in the README that real catalog integration requires replacing `catalog.json` with a live API connector.

## Risk 2 — YOLOv8 Does Not Reliably Detect Eyewear

**Problem:** Standard YOLOv8 models are trained on COCO classes. Sunglasses are a COCO class (class 77), but detection confidence varies significantly with image quality and framing.

**Impact:** The cropping step may be skipped for many real-world images, reducing attribute extraction accuracy.

**Mitigation:** Use Grounding DINO as a fallback when YOLOv8 returns no eyewear detections. Grounding DINO accepts text prompts and can detect "glasses" or "sunglasses" by description rather than fixed class IDs. If both fail, proceed with the full image and rely on the vision model's ability to locate eyewear within a cluttered scene.

## Risk 3 — Web Search Returns Insufficient Evidence

**Problem:** For obscure or recently released movies/celebrities, Tavily or other search APIs may return little relevant content.

**Impact:** Style DNA confidence will be low, triggering the low-confidence fallback path.

**Mitigation:** The retry strategy (Section 11.9) handles this gracefully. The system always falls back to direct style search if web evidence is insufficient. Select demo test queries (the "Akshay Khanna in Dhurandhar" example) in advance and verify they produce usable web search results before demo day.

## Risk 4 — LLM API Latency Accumulates

**Problem:** A single NL search may involve 3–5 sequential LLM calls (intent extraction, style DNA synthesis, evidence validation). At 3–5 seconds per call, total latency can reach 20–30 seconds.

**Impact:** Users who do not see feedback will assume the system is broken.

**Mitigation:** SSE heartbeat events every 3 seconds maintain the perception of progress. The ProgressStream component with step-by-step animations makes 20 seconds feel shorter. Cache model outputs per session_id so that repeated queries within a session do not re-invoke the same LLM calls.

## Risk 5 — No Real PDP or Cart Integration

**Problem:** The actual Magrabi eCommerce PDP and cart are not accessible.

**Impact:** The demo cannot show a real purchase flow.

**Mitigation:** Build a mock PDP component in the React app for each catalog product. The PDP shows the product image, attributes, price, and a working "Add to Cart" button. The cart is implemented as React state — a sidebar panel shows accumulated cart items and a total. This is entirely acceptable for a hackathon demo.

## Risk 6 — Embedding Drift

**Problem:** The vision model may describe product attributes in language that differs from the catalog's attribute vocabulary even after normalization.

**Impact:** Cosine similarity scores are lower than they should be, reducing ranking quality.

**Mitigation (hackathon scope):** Test the normalization dictionary against a sample of 20 vision model outputs before building the demo scenarios, and add any missing synonyms to the dictionary. This is the highest-ROI fix in the available time.

**Post-Hackathon Extension:** At catalog ingestion time, embed two versions of each product's text: the standard version and a synonym-augmented version. Use the maximum similarity across both when ranking. This is a meaningful quality improvement but takes more engineering time than the hackathon allows.

---

# 15. Evaluation Checklist

Use this checklist in the 30 minutes before demo recording. Every unchecked item is a lost mark.

## MCP Architecture (20 marks)

- [ ] React client sends a structured MCPRequest to the FastAPI server via HTTP POST
- [ ] Client never directly imports or calls any tool, model, or intelligence module
- [ ] Tool Router is the only entry point to tool execution — orchestrator calls router, not tools
- [ ] Context Manager maintains session state correctly across at least 3 turns in one session
- [ ] SSE stream emits at least 5 distinct labeled step events before the final result
- [ ] Session isolation verified: two browser tabs with different session_ids cannot access each other's state
- [ ] Error recovery layer demonstrated at least once in the demo (show a graceful fallback)

## Image Matching Intelligence (20 marks)

- [ ] Background removal applied before attribute extraction (show a before/after in the demo if possible)
- [ ] Object detection cropping demonstrated with a real-world photo
- [ ] Attribute normalization dictionary applied — "golden" and "gold" both find the same products
- [ ] Hybrid scoring formula used — score_breakdown shown in the UI for at least one product
- [ ] Confidence Governance threshold check working — results below 0.5 confidence show "Here are some alternatives" message
- [ ] Explainability output shown on every product card
- [ ] Fallback search chain triggered with a deliberately ambiguous image

## Natural Language Understanding (15 marks)

- [ ] Intent schema extracted and shown in the UI (as a debug panel or console log during demo)
- [ ] Query decomposed into at least 3 distinct search queries (visible in the SSE steps)
- [ ] Evidence validation step shown — system rejects single-source evidence
- [ ] Style DNA synthesized and shown to user (brief UI card showing extracted attributes)
- [ ] Conversational follow-up ("cheaper options") resolved using session memory without re-searching

## Product Mapping Accuracy (15 marks)

- [ ] Mock catalog contains 30+ products with full attribute coverage
- [ ] Every product has an embedding in ChromaDB (verify via startup log)
- [ ] Top-3 results always returned — no empty result set in any demo flow
- [ ] All products link to a mock PDP page
- [ ] Mock PDP has a working "Add to Cart" button
- [ ] Cart panel shows accumulated items and total

## UX & User Engagement (15 marks)

- [ ] Progress stream animates step by step during all processing
- [ ] Skeleton loaders visible during processing (not just a spinner)
- [ ] Heartbeat event triggers a pulse animation when a step takes longer than 3 seconds
- [ ] No blank or error screen at any point during the demo
- [ ] Recommendation strip (budget / premium / trending) visible below main results
- [ ] Follow-up chat input is accessible immediately after results are shown

## Code Quality & Modularity (10 marks)

- [ ] Each tool file contains exactly one tool class with one clear responsibility
- [ ] No tool file imports from any other tool file
- [ ] All API keys loaded from environment variables — no hardcoded values
- [ ] README documents every environment variable required
- [ ] `inputs/` folder contains at least 5 test images and 5 test queries
- [ ] Docker Compose starts the entire stack with one command

## Demo Clarity (5 marks)

- [ ] Video is under 15 minutes
- [ ] All four main flows shown: image search, NL search, conversational refinement, architecture callout
- [ ] `/metrics` endpoint briefly shown as evidence of observability design
- [ ] PDP navigation and cart visible
- [ ] No hardcoded or pre-computed results — every demo result is computed live
- [ ] Architecture overview given at the start

## Bonus Marks

- [ ] Real-time streaming responses visible as step-by-step SSE events (+3)
- [ ] Multi-image upload: user can upload 2 images and system finds products matching both (+2)
- [ ] Recommendation strip showing budget / premium / trending alternatives (+2)
- [ ] Voice input for NL queries, or animated Style DNA visualization (+3)

---

*End of Vision-to-Cart Implementation Plan V4 — Simplified for Hackathon*
*Architecture diagram: `HLD_diagram_hackathon_v4.png`*
*Scope: Hackathon · Timebox: 8 Hours · Mandatory Deliverables: End-to-End Pipeline + Confidence + Error Recovery + Docker Compose + 3 Demo Scenarios*

---
