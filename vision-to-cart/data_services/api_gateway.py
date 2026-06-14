import os
import json
import time
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
import redis

app = FastAPI(title="Vision-to-Cart Zone 1 API Gateway", version="4.0")

# Redis configuration with local in-memory fallback
redis_client = None
try:
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True, socket_connect_timeout=2)
    redis_client.ping()
    print("API Gateway: Connected to Redis cache service.")
except Exception:
    print("API Gateway: Redis connection failed. Falling back to In-Memory Cache.")
    redis_client = None

# Fallback in-memory cache
in_memory_cache: Dict[str, Dict[str, Any]] = {}

# Load local static catalog as default store
CATALOG_PATH = os.getenv("CATALOG_PATH", os.path.join(os.path.dirname(__file__), "catalog", "catalog.json"))
catalog_cache: List[Dict[str, Any]] = []

def load_catalog() -> List[Dict[str, Any]]:
    global catalog_cache
    if catalog_cache:
        return catalog_cache
    try:
        if os.path.exists(CATALOG_PATH):
            with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                catalog_cache = json.load(f)
                return catalog_cache
    except Exception as e:
        print(f"Error loading catalog.json: {e}")
    return []

# Unified Response Envelope Helper
def standard_response(data: Any, error: Optional[str] = None, latency_ms: float = 0.0) -> Dict[str, Any]:
    return {
        "status": "error" if error else "success",
        "data": data,
        "error": error,
        "latency_ms": round(latency_ms, 2)
    }

# Rate Limiter stub (Simulated per session limit)
session_rate_limits: Dict[str, int] = {}
MAX_REQUESTS_PER_MINUTE = 60

def is_rate_limited(session_id: str) -> bool:
    if not session_id:
        return False
    current_time = int(time.time() / 60)
    key = f"{session_id}:{current_time}"
    session_rate_limits[key] = session_rate_limits.get(key, 0) + 1
    return session_rate_limits[key] > MAX_REQUESTS_PER_MINUTE

@app.middleware("http")
async def process_time_and_rate_limit(request: Request, call_next):
    start_time = time.time()
    session_id = request.headers.get("x-session-id", "default")
    
    if is_rate_limited(session_id):
        return Response(
            content=json.dumps(standard_response(None, "Rate limit exceeded (Max 60 req/min)", 0)),
            status_code=429,
            media_type="application/json"
        )
    
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    response.headers["X-Response-Time-Ms"] = str(round(duration_ms, 2))
    return response

# Standard Schemas
class CacheRequest(BaseModel):
    key: str
    value: Any
    ttl_seconds: Optional[int] = 300

class QueryRequest(BaseModel):
    query_text: str
    filters: Optional[Dict[str, Any]] = None

@app.get("/health")
def health_check():
    return standard_response({"status": "healthy", "redis_connected": redis_client is not None})

@app.get("/products")
def get_all_products(shape: Optional[str] = None, brand: Optional[str] = None):
    start = time.time()
    products = load_catalog()
    
    # Filter catalog
    filtered = []
    for p in products:
        if shape and p.get("shape", "").lower() != shape.lower():
            continue
        if brand and p.get("brand", "").lower() != brand.lower():
            continue
        filtered.append(p)
        
    return standard_response(filtered, latency_ms=(time.time() - start) * 1000)

@app.get("/products/{product_id}")
def get_product(product_id: str):
    start = time.time()
    products = load_catalog()
    for p in products:
        if p.get("product_id") == product_id:
            return standard_response(p, latency_ms=(time.time() - start) * 1000)
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/cache/get")
def get_cache(payload: Dict[str, str]):
    start = time.time()
    key = payload.get("key")
    if not key:
        return standard_response(None, "Missing key parameter", (time.time() - start) * 1000)
    
    # Check Redis
    if redis_client:
        try:
            val = redis_client.get(key)
            if val:
                return standard_response(json.loads(val), latency_ms=(time.time() - start) * 1000)
        except Exception as e:
            print(f"Redis cache fetch error: {e}")
            
    # Check In-Memory fallback
    if key in in_memory_cache:
        cached = in_memory_cache[key]
        if cached["expiry"] > time.time():
            return standard_response(cached["value"], latency_ms=(time.time() - start) * 1000)
        else:
            del in_memory_cache[key]
            
    return standard_response(None, "Cache miss", (time.time() - start) * 1000)

@app.post("/cache/set")
def set_cache(payload: CacheRequest):
    start = time.time()
    # Save in Redis
    if redis_client:
        try:
            redis_client.setex(payload.key, payload.ttl_seconds, json.dumps(payload.value))
            return standard_response(True, latency_ms=(time.time() - start) * 1000)
        except Exception as e:
            print(f"Redis cache save error: {e}")
            
    # Save In-Memory fallback
    in_memory_cache[payload.key] = {
        "value": payload.value,
        "expiry": time.time() + payload.ttl_seconds
    }
    return standard_response(True, latency_ms=(time.time() - start) * 1000)
