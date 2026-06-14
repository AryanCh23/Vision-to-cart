import os
import json
import asyncio
import time
import redis
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Absolute imports
from mcp_server.orchestrator import Orchestrator
from mcp_server.observability import record_metric, get_metrics

# Redis configuration with local in-memory fallback
redis_client = None
try:
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True, socket_connect_timeout=2)
    redis_client.ping()
    print("MCP Server: Connected to Redis cache service.")
except Exception as e:
    print(f"MCP Server: Redis connection failed: {e}. Falling back to In-Memory Cache.")
    redis_client = None

# Fallback in-memory cache
in_memory_cache: Dict[str, Dict[str, Any]] = {}

app = FastAPI(title="Vision-to-Cart MCP Server", version="4.0")

# Allow all origins so the frontend HTML file can connect directly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CacheGetPayload(BaseModel):
    key: str

class CacheSetPayload(BaseModel):
    key: str
    value: Any
    ttl_seconds: Optional[int] = 300

class CartAddRequest(BaseModel):
    session_id: str
    product_id: str

class CartRemoveRequest(BaseModel):
    session_id: str
    product_id: str

class CartClearRequest(BaseModel):
    session_id: str

class MCPRequest(BaseModel):
    session_id: str = Field(..., example="session_abc123")
    input_type: str = Field(..., example="text") # "text" or "image"
    image_base64: Optional[str] = Field(None, description="Base64 encoded image string if input_type is 'image'")
    text_query: Optional[str] = Field(None, description="Natural language search query if input_type is 'text'")

# Basic security guards
def validate_request(payload: MCPRequest):
    if not payload.session_id.isalnum():
        raise HTTPException(status_code=400, detail="Invalid session_id. Must be alphanumeric.")
    if payload.input_type not in ["text", "image"]:
        raise HTTPException(status_code=400, detail="input_type must be 'text' or 'image'.")
    if payload.input_type == "text" and not payload.text_query:
        raise HTTPException(status_code=400, detail="text_query is required for text input_type.")
    if payload.input_type == "image" and not payload.image_base64:
        raise HTTPException(status_code=400, detail="image_base64 is required for image input_type.")
        
    # Check payload size limits (e.g. max 10MB base64)
    if payload.image_base64 and len(payload.image_base64) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size exceeds maximum allowed limit (10MB).")

@app.get("/")
def index():
    return {"name": "Vision-to-Cart MCP Server", "status": "active"}

@app.get("/metrics")
def metrics_endpoint():
    return get_metrics()

@app.post("/mcp/stream")
async def mcp_stream_endpoint(payload: MCPRequest):
    """
    Accepts search requests and yields server-sent events (SSE) representing
    processing steps and the final recommendations.
    """
    validate_request(payload)
    record_metric("requests_received", 1)
    
    orchestrator = Orchestrator()
    
    async def event_generator():
        try:
            async for event in orchestrator.execute_pipeline_stream(payload):
                # Standard SSE format: "data: <json>\n\n"
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            err_event = {
                "event_type": "error",
                "label": "Pipeline Execution Failed",
                "data": {"detail": str(e)}
            }
            yield f"data: {json.dumps(err_event)}\n\n"
            record_metric("pipeline_errors", 1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/cache/get")
def get_cache(payload: CacheGetPayload):
    key = payload.key
    if redis_client:
        try:
            val = redis_client.get(key)
            if val:
                return {"status": "success", "data": json.loads(val)}
        except Exception as e:
            print(f"Redis cache fetch error: {e}")
            
    if key in in_memory_cache:
        cached = in_memory_cache[key]
        if cached["expiry"] > time.time():
            return {"status": "success", "data": cached["value"]}
        else:
            del in_memory_cache[key]
            
    return {"status": "error", "error": "Cache miss"}

@app.post("/cache/set")
def set_cache(payload: CacheSetPayload):
    key = payload.key
    if redis_client:
        try:
            redis_client.setex(key, payload.ttl_seconds, json.dumps(payload.value))
            return {"status": "success", "data": True}
        except Exception as e:
            print(f"Redis cache save error: {e}")
            
    in_memory_cache[key] = {
        "value": payload.value,
        "expiry": time.time() + payload.ttl_seconds
    }
    return {"status": "success", "data": True}

@app.get("/products")
def get_products():
    catalog_path = os.getenv("CATALOG_PATH", "data_services/catalog/catalog.json")
    try:
        if os.path.exists(catalog_path):
            with open(catalog_path, "r", encoding="utf-8") as f:
                products = json.load(f)
                return {"status": "success", "data": products}
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
    return {"status": "success", "data": []}

@app.get("/products/{product_id}")
def get_product(product_id: str):
    catalog_path = os.getenv("CATALOG_PATH", "data_services/catalog/catalog.json")
    try:
        if os.path.exists(catalog_path):
            with open(catalog_path, "r", encoding="utf-8") as f:
                products = json.load(f)
                for p in products:
                    if p.get("product_id") == product_id:
                        return {"status": "success", "data": p}
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/cart/add")
async def api_add_to_cart(req: CartAddRequest):
    from mcp_server.tool_router import ToolRouter
    router = ToolRouter()
    payload = {"action": "add_to_cart", "product_id": req.product_id, "session_id": req.session_id}
    res = await router.call_tool("pdp_cart_checkout_tool", payload)
    return res

@app.post("/cart/remove")
async def api_remove_from_cart(req: CartRemoveRequest):
    from mcp_server.tool_router import ToolRouter
    router = ToolRouter()
    payload = {"action": "remove_from_cart", "product_id": req.product_id, "session_id": req.session_id}
    res = await router.call_tool("pdp_cart_checkout_tool", payload)
    return res

@app.post("/cart/clear")
async def api_clear_cart(req: CartClearRequest):
    from mcp_server.tool_router import ToolRouter
    router = ToolRouter()
    payload = {"action": "clear_cart", "session_id": req.session_id}
    res = await router.call_tool("pdp_cart_checkout_tool", payload)
    return res

@app.get("/cart")
async def api_get_cart(session_id: str = "default"):
    from mcp_server.tool_router import ToolRouter
    router = ToolRouter()
    payload = {"action": "get_cart", "session_id": session_id}
    res = await router.call_tool("pdp_cart_checkout_tool", payload)
    return res

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("mcp_server.main:app", host="0.0.0.0", port=port, reload=True)
