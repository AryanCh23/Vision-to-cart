from typing import Dict, Any, List

def evaluate_confidence(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Applies the V4 simplified single 0.5 threshold logic for confidence governance.
    Returns matches along with a governance tier and message.
    """
    if not matches:
        return {
            "matches": [],
            "top_confidence": 0.0,
            "confidence_tier": "Low",
            "governance_message": "No matching products found."
        }

    # Top match score
    top_score = matches[0].get("match_score", 0.0)

    if top_score >= 0.5:
        # Standard high/medium confidence presentation
        tier = "High" if top_score >= 0.8 else "Medium"
        message = "Found matching products from our catalog."
    else:
        # Low confidence fallback notification
        tier = "Low"
        message = "We couldn't find an exact match, but here are some alternatives you might like:"

    # Update confidence tier on each match item for UI representation
    for m in matches:
        score = m.get("match_score", 0.0)
        if score >= 0.8:
            m["confidence_tier"] = "High"
        elif score >= 0.5:
            m["confidence_tier"] = "Medium"
        else:
            m["confidence_tier"] = "Low"

    return {
        "matches": matches,
        "top_confidence": top_score,
        "confidence_tier": tier,
        "governance_message": message
    }
