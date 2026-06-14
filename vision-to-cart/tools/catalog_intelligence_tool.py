import os
import json
from typing import Dict, Any, List

# Project root — always resolved relative to this file
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Core database utility
from intelligence.product_intelligence import ProductIntelligence

def run_catalog_intelligence(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enriches catalog products with style taxonomy classification and ingests them
    into ChromaDB (vector store) and standard databases.
    """
    catalog_path = payload.get("catalog_path")
    if not catalog_path or not os.path.exists(catalog_path):
        # Default fallback — use absolute path from project root
        catalog_path = os.getenv(
            "CATALOG_PATH",
            os.path.join(PROJECT_ROOT, "data_services", "catalog", "catalog.json")
        )

    print(f"CatalogIntelligenceTool: Loading raw catalog from {catalog_path}...")
    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            products = json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to read catalog JSON: {e}")

    print("CatalogIntelligenceTool: Applying taxonomy classification rules...")
    enriched_products = []
    for p in products:
        enriched = enrich_product(p)
        enriched_products.append(enriched)

    # Save enriched catalog
    enriched_path = os.getenv(
        "ENRICHED_CATALOG_PATH",
        os.path.join(PROJECT_ROOT, "data_services", "catalog", "catalog_enriched.json")
    )
    try:
        os.makedirs(os.path.dirname(enriched_path), exist_ok=True)
        with open(enriched_path, "w", encoding="utf-8") as f:
            json.dump(enriched_products, f, indent=2)
        print(f"CatalogIntelligenceTool: Saved enriched products to {enriched_path}")
    except Exception as e:
        print(f"Warning: Could not save enriched JSON to disk: {e}")

    # Vectorize and ingest
    print("CatalogIntelligenceTool: Generating embeddings and loading into Vector DB...")
    pi = ProductIntelligence()
    success = pi.ingest_catalog(enriched_products)

    return {
        "status": "success" if success else "partial",
        "products_processed": len(enriched_products),
        "vector_store_populated": success
    }

def enrich_product(p: Dict[str, Any]) -> Dict[str, Any]:
    """Assigns custom classification tags (style classification, trend score) for V4 taxonomy."""
    p_copy = p.copy()
    
    # Standardize style tags into a primary taxonomy class
    tags = [t.lower() for t in p_copy.get("style_tags", [])]
    
    # 1. Style Taxonomy classification mapping
    if "luxury" in tags or "prestige" in tags:
        p_copy["style_taxonomy_tag"] = "classic-luxury"
    elif "sporty" in tags or "performance" in tags:
        p_copy["style_taxonomy_tag"] = "sport-performance"
    elif "trendy" in tags or "bold" in tags:
        p_copy["style_taxonomy_tag"] = "fashion-forward"
    elif "minimalist" in tags or "clean" in tags:
        p_copy["style_taxonomy_tag"] = "minimalist-clean"
    else:
        p_copy["style_taxonomy_tag"] = "casual-everyday"

    # 2. Trend Score assigning (0-100) based on style trends
    popularity = p_copy.get("popularity_score", 50)
    if p_copy["style_taxonomy_tag"] in ["fashion-forward", "classic-luxury"]:
        p_copy["trend_score"] = int(min(100, popularity * 1.05 + 5))
    else:
        p_copy["trend_score"] = int(popularity * 0.95)

    # 3. Gender Affinity enrichment
    gender = p_copy.get("gender", "unisex").lower()
    if gender == "male":
        p_copy["gender_affinity"] = "masculine"
    elif gender == "female":
        p_copy["gender_affinity"] = "feminine"
    else:
        p_copy["gender_affinity"] = "neutral"

    return p_copy
