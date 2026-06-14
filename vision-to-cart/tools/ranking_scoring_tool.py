from typing import Dict, Any, List
from intelligence.style_dna import StyleDNA

def run_ranking_scoring(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Executes the 5-component re-ranking formula:
    Final Score = (40% Vector + 20% Shape + 15% Brand + 15% Lens + 10% Metadata) * Popularity weight
    """
    candidates = payload.get("candidates", [])
    dna_dict = payload.get("style_dna")
    
    if not dna_dict:
        raise ValueError("Missing 'style_dna' in scoring payload.")
        
    dna = StyleDNA(**dna_dict)
    scored_matches = []

    for item in candidates:
        p = item.get("product", item)
        vector_score = item.get("vector_score", 0.5)
        
        # 1. Embedding Similarity (40%)
        w_vector = 0.40
        s_vector = vector_score

        # 2. Shape Match (20%)
        w_shape = 0.20
        s_shape = 0.0
        dna_shape = dna.shape.lower() if dna.shape else ""
        prod_shape = p.get("shape", "").lower()
        if dna_shape and prod_shape:
            if dna_shape == prod_shape:
                s_shape = 1.0
            elif (dna_shape in ["aviator", "teardrop"] and prod_shape in ["aviator", "teardrop"]) or \
                 (dna_shape in ["square", "rectangle"] and prod_shape in ["square", "rectangle"]):
                # Same family
                s_shape = 0.5

        # 3. Brand Match (15%)
        # If no brand hint, weight is redistributed to Vector (+10%) and Shape (+5%)
        w_brand = 0.15
        s_brand = 0.0
        dna_brand = dna.brand_hint.lower() if dna.brand_hint else ""
        prod_brand = p.get("brand", "").lower()
        
        if not dna_brand:
            # Redistribution
            w_vector += 0.10
            w_shape += 0.05
            w_brand = 0.0
        elif dna_brand == prod_brand:
            s_brand = 1.0

        # 4. Lens Color Match (15%)
        w_lens = 0.15
        s_lens = 0.0
        dna_lens = dna.lens_color.lower() if dna.lens_color else ""
        prod_lens = p.get("lens_color", "").lower()
        if dna_lens and prod_lens:
            if dna_lens == prod_lens:
                s_lens = 1.0
            elif dna_lens in ["black", "gray", "dark"] and prod_lens in ["black", "gray", "dark"]:
                s_lens = 0.5
            elif dna_lens in ["brown", "amber", "gold"] and prod_lens in ["brown", "amber", "gold"]:
                s_lens = 0.5

        # 5. Metadata Match (10%)
        w_meta = 0.10
        s_meta = 0.0
        
        dna_tags = set(t.lower() for t in dna.style_tags)
        prod_tags = set(t.lower() for t in p.get("style_tags", []))
        
        if dna_tags and prod_tags:
            intersection = dna_tags.intersection(prod_tags)
            union = dna_tags.union(prod_tags)
            s_meta += (len(intersection) / len(union)) * 0.7 # Jaccard similarity counts for 70% of meta score
            
        # Material match bonus (30% of meta score)
        dna_mat = dna.frame_material.lower() if dna.frame_material else ""
        prod_mat = p.get("frame_material", "").lower()
        if dna_mat and prod_mat and dna_mat == prod_mat:
            s_meta += 0.3
            
        # Calculate base hybrid score (0-1)
        base_score = (w_vector * s_vector) + (w_shape * s_shape) + (w_brand * s_brand) + (w_lens * s_lens) + (w_meta * s_meta)
        
        # Popularity multiplier: static popularity score (1-100) maps to minor boost multiplier (0.9 to 1.1)
        popularity = p.get("popularity_score", 50)
        pop_weight = 0.9 + (popularity / 500.0) # maps 0-100 to 0.9-1.1
        final_score = min(1.0, base_score * pop_weight)

        # Build human-readable match reasoning
        match_details = []
        if s_shape == 1.0: match_details.append(f"{p.get('shape')} shape")
        if s_lens == 1.0: match_details.append(f"{p.get('lens_color')} lenses")
        if s_brand == 1.0: match_details.append(f"brand {p.get('brand')}")
        if s_meta >= 0.5: match_details.append("matching style aesthetics")
        
        reason = "Matched because: " + (", ".join(match_details) if match_details else "high semantic similarity")
        reason += f" — Confidence Score: {int(final_score * 100)}%"

        scored_matches.append({
            "product_id": p.get("product_id"),
            "name": p.get("name"),
            "brand": p.get("brand"),
            "shape": p.get("shape"),
            "frame_color": p.get("frame_color"),
            "lens_color": p.get("lens_color"),
            "frame_material": p.get("frame_material"),
            "price": p.get("price"),
            "pdp_url": p.get("pdp_url"),
            "image_url": p.get("image_url"),
            "match_score": final_score,
            "match_reason": reason,
            "polarized": p.get("polarized", False),
            "uv_protection": p.get("uv_protection", "UV400"),
            "weight_grams": p.get("weight_grams", 30),
            "warranty_years": p.get("warranty_years", 2),
            "celebrity_worn": p.get("celebrity_worn"),
            "description": p.get("description"),
            "rating": p.get("rating", 4.5),
            "review_count": p.get("review_count", 100),
            "scenario": p.get("scenario", []),
            "face_shape_fit": p.get("face_shape_fit", [])
        })

    # Sort candidates by final score descending
    scored_matches.sort(key=lambda x: x["match_score"], reverse=True)
    return scored_matches
