from typing import Dict, Any, List

# Core database utility
from intelligence.product_intelligence import ProductIntelligence
from intelligence.style_dna import StyleDNA

def run_search_retrieval(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Executes search and retrieval:
    StyleDNA -> search string -> ChromaDB vector query -> post-filtering by hard constraints (brand/gender/price).
    """
    dna_dict = payload.get("style_dna")
    limit = payload.get("limit", 10)
    
    if not dna_dict:
        raise ValueError("Missing 'style_dna' in search payload.")

    # Convert back to StyleDNA object
    dna = StyleDNA(**dna_dict)
    
    # 1. Compile search representation
    search_text = dna.to_search_text()
    print(f"SearchRetrievalTool: Combined search text -> '{search_text}'")

    # 2. Vector search query
    pi = ProductIntelligence()
    candidates = pi.query_vector_search(search_text, top_k=limit * 2)
    print(f"SearchRetrievalTool: Vector search retrieved {len(candidates)} raw matches.")

    # 3. Apply Metadata filtering
    filtered_candidates = []
    for item in candidates:
        p = item["product"]
        vector_score = item["vector_score"]

        # Gender constraint filtering
        if dna.gender and dna.gender != "unisex" and p.get("gender") != "unisex":
            if dna.gender != p.get("gender"):
                # Skip products that don't match gender
                continue

        # Brand hint filtering (soft-constraint: if brand_hint is set, we don't hard-fail, we rank higher later,
        # but if user specifically says "Ray-Ban only", we can filter. Let's keep it soft/hybrid)
        
        # Price tier constraint filtering
        price = p.get("price", 0)
        price_pref = dna.price_range_preference
        if price_pref:
            if price_pref == "budget" and price > 4000:
                continue
            elif price_pref == "premium" and price < 8000:
                continue

        filtered_candidates.append(item)

    print(f"SearchRetrievalTool: Returning {len(filtered_candidates[:limit])} filtered candidates.")
    return filtered_candidates[:limit]
