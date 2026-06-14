from typing import Dict, Any, List

# Core router helper
from data_services.data_services_router import DataServicesRouter
from intelligence.style_dna import StyleDNA

def run_recommendation(payload: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Returns alternative recommendations:
    - Budget: Same shape/style, lower price.
    - Premium: Luxury brand or higher price, similar shape.
    - Trending: Matches style_taxonomy_tag, high popularity_score.
    """
    ranked_matches = payload.get("ranked_matches", [])
    dna_dict = payload.get("style_dna")
    
    if not ranked_matches:
        return {"budget": [], "premium": [], "trending": []}
        
    top_match = ranked_matches[0]
    top_match_id = top_match.get("product_id")
    top_price = top_match.get("price", 5000)
    top_shape = top_match.get("shape", "")

    # Retrieve all products from database router
    router = DataServicesRouter()
    all_products = router.get_all_products()
    
    budget_options = []
    premium_options = []
    trending_options = []
    
    for p in all_products:
        # Avoid recommending the top match itself
        if p.get("product_id") == top_match_id:
            continue
            
        p_price = p.get("price", 0)
        p_shape = p.get("shape", "")
        
        # 1. Budget Option: same shape, price is cheaper by at least 20%
        if p_shape == top_shape and p_price < top_price * 0.8:
            budget_options.append(p)
            
        # 2. Premium Option: same shape, price is more expensive by at least 30% or a luxury brand
        if p_shape == top_shape and (p_price > top_price * 1.3 or p.get("brand") in ["Gucci", "Cartier", "Prada"]):
            # Filter if already matches budget rules
            if p not in budget_options:
                premium_options.append(p)
                
        # 3. Trending Option: high popularity (>85) and similar style_tags
        p_tags = set(t.lower() for t in p.get("style_tags", []))
        top_tags = set(top_match.get("style_tags", [])) if "style_tags" in top_match else set()
        
        # Check overlaps
        if p.get("popularity_score", 0) >= 85 or p_tags.intersection(top_tags):
            if p.get("product_id") != top_match_id and p not in budget_options and p not in premium_options:
                trending_options.append(p)

    # Sort alternatives
    budget_options.sort(key=lambda x: x.get("price", 0))
    premium_options.sort(key=lambda x: x.get("price", 0), reverse=True)
    trending_options.sort(key=lambda x: x.get("popularity_score", 0), reverse=True)

    # Clean outputs (only return top 2 for each category)
    def clean_format(lst: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "product_id": item.get("product_id"),
                "name": item.get("name"),
                "brand": item.get("brand"),
                "price": item.get("price"),
                "pdp_url": item.get("pdp_url"),
                "image_url": item.get("image_url")
            }
            for item in lst[:2]
        ]

    return {
        "budget": clean_format(budget_options),
        "premium": clean_format(premium_options),
        "trending": clean_format(trending_options)
    }
