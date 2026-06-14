import os
import requests
import time
from typing import Dict, Any, List, Optional

# Module-level shared process-wide fallback cache
_LOCAL_CACHE: Dict[str, Any] = {}
_LOCAL_CACHE_EXPIRY: Dict[str, float] = {}

class DataServicesRouter:
    """
    Client router that interfaces between MCP server/tools and Zone 1 services.
    Attempts to use the API Gateway if running, otherwise falls back to direct local files/libraries.
    """
    def __init__(self, api_gateway_url: str = "http://localhost:8000"):
        self.api_gateway_url = api_gateway_url
        self.local_catalog_path = os.getenv("CATALOG_PATH", "data_services/catalog/catalog.json")

    def _call_gateway(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        url = f"{self.api_gateway_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=2)
            else:
                response = requests.post(url, json=payload, timeout=2)
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    return result.get("data")
        except Exception:
            # Silence gateway error to fallback locally
            pass
        return None

    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        # Try API Gateway first
        data = self._call_gateway("GET", f"/products/{product_id}")
        if data:
            return data
            
        # Fallback to direct local JSON read
        try:
            import json
            if os.path.exists(self.local_catalog_path):
                with open(self.local_catalog_path, "r", encoding="utf-8") as f:
                    products = json.load(f)
                    for p in products:
                        if p.get("product_id") == product_id:
                            return p
        except Exception as e:
            print(f"Direct catalog lookup error: {e}")
        return None

    def get_all_products(self, shape: Optional[str] = None, brand: Optional[str] = None) -> List[Dict[str, Any]]:
        # Try API Gateway first
        params = []
        if shape: params.append(f"shape={shape}")
        if brand: params.append(f"brand={brand}")
        query_str = "?" + "&".join(params) if params else ""
        
        data = self._call_gateway("GET", f"/products{query_str}")
        if data:
            return data
            
        # Fallback to direct local JSON read
        try:
            import json
            if os.path.exists(self.local_catalog_path):
                with open(self.local_catalog_path, "r", encoding="utf-8") as f:
                    products = json.load(f)
                    filtered = []
                    for p in products:
                        if shape and p.get("shape", "").lower() != shape.lower():
                            continue
                        if brand and p.get("brand", "").lower() != brand.lower():
                            continue
                        filtered.append(p)
                    return filtered
        except Exception as e:
            print(f"Direct catalog list error: {e}")
        return []

    def get_cache(self, key: str) -> Optional[Any]:
        # Try API Gateway first
        data = self._call_gateway("POST", "/cache/get", {"key": key})
        if data is not None:
            return data
            
        # Fallback to local process-wide cache
        global _LOCAL_CACHE, _LOCAL_CACHE_EXPIRY
        if key in _LOCAL_CACHE:
            expiry = _LOCAL_CACHE_EXPIRY.get(key, 0)
            if expiry > time.time():
                print(f"DataServicesRouter: Cache HIT (local fallback) for key '{key}'")
                return _LOCAL_CACHE[key]
            else:
                print(f"DataServicesRouter: Cache EXPIRED (local fallback) for key '{key}'")
                del _LOCAL_CACHE[key]
                if key in _LOCAL_CACHE_EXPIRY:
                    del _LOCAL_CACHE_EXPIRY[key]
        return None

    def set_cache(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        # Try API Gateway first
        res = self._call_gateway("POST", "/cache/set", {"key": key, "value": value, "ttl_seconds": ttl_seconds})
        if res is not None:
            return True
            
        # Fallback to local process-wide cache
        global _LOCAL_CACHE, _LOCAL_CACHE_EXPIRY
        print(f"DataServicesRouter: Cache SET (local fallback) for key '{key}' (TTL: {ttl_seconds}s)")
        _LOCAL_CACHE[key] = value
        _LOCAL_CACHE_EXPIRY[key] = time.time() + ttl_seconds
        return True
