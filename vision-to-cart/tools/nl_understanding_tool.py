import os
import re
import requests
from typing import Dict, Any, List

# Schema and StyleDNA imports
from intelligence.intent_schema import IntentSchema
from intelligence.style_dna import StyleDNA
from intelligence.normalization import normalize_attribute, normalize_style_tags

def run_nl_understanding(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs the Natural Language Understanding pipeline:
    Query Text -> Intent Extraction -> Web Search (Evidence) -> StyleDNA Synthesis
    """
    text_query = payload.get("text_query", "")
    if not text_query:
        raise ValueError("Missing 'text_query' in payload.")

    print(f"NLUnderstandingTool: Analyzing query '{text_query}'...")
    
    # Step 1: Intent Extraction (LLM or heuristic fallback)
    intent = extract_intent(text_query)
    print(f"NLUnderstandingTool: Extracted Intent -> {intent.dict_summary()}")

    # Step 2: Web Search for evidence (e.g. Daniel Craig Skyfall -> Tom Ford Snowdon, dark acetate square)
    evidence_list = []
    if intent.celebrity_name or intent.movie_name or intent.event_name:
        evidence_list = perform_web_search(intent)
        print(f"NLUnderstandingTool: Gathered {len(evidence_list)} pieces of web evidence.")
        
        # Refine intent using evidence
        enrich_intent_from_evidence(intent, evidence_list)
        
    # Step 3: Synthesize into StyleDNA
    style_dna = StyleDNA(
        shape=normalize_attribute("shape", intent.shape_preference),
        frame_color=normalize_attribute("color", intent.color_preference),
        lens_color=normalize_attribute("color", intent.color_preference), # default lens color
        frame_material=normalize_attribute("material", None),
        gender=intent.gender_preference or "unisex",
        style_tags=normalize_style_tags(intent.style_descriptors),
        brand_hint=intent.brand_hint,
        price_range_preference=intent.price_refinement,
        confidence_score=0.90 if evidence_list else 0.75,
        source="nl"
    )

    return {
        "style_dna": style_dna.__dict__,
        "evidence": evidence_list
    }

def extract_intent(query: str) -> IntentSchema:
    """Uses regex rules to extract search metadata from queries for robust mock validation."""
    query_lower = query.lower()
    intent = IntentSchema()

    # Brand extraction
    if "ray-ban" in query_lower or "rayban" in query_lower:
        intent.brand_hint = "Ray-Ban"
    elif "oakley" in query_lower:
        intent.brand_hint = "Oakley"
    elif "gucci" in query_lower:
        intent.brand_hint = "Gucci"
    elif "cartier" in query_lower:
        intent.brand_hint = "Cartier"

    # Celebrity / Movie extraction
    if "daniel craig" in query_lower or "james bond" in query_lower:
        intent.celebrity_name = "Daniel Craig"
        intent.movie_name = "Skyfall"
        intent.style_descriptors.append("classic")
        intent.style_descriptors.append("luxury")
    elif "tony stark" in query_lower or "iron man" in query_lower or "robert downey" in query_lower:
        intent.celebrity_name = "Robert Downey Jr."
        intent.movie_name = "Iron Man 3"
        intent.style_descriptors.append("bold")
        intent.style_descriptors.append("trendy")

    # Shape matching
    shapes = ["aviator", "round", "rectangle", "cat-eye", "oval", "sport", "square"]
    for s in shapes:
        if s in query_lower:
            intent.shape_preference = s
            break

    # Color matching
    colors = ["gold", "silver", "black", "brown", "clear", "blue", "green", "gray", "red", "pink", "yellow"]
    for c in colors:
        if c in query_lower:
            intent.color_preference = c
            break

    # Price refinements
    if "cheap" in query_lower or "budget" in query_lower or "low cost" in query_lower:
        intent.price_refinement = "budget"
    elif "premium" in query_lower or "expensive" in query_lower or "luxury" in query_lower:
        intent.price_refinement = "premium"

    # Gender preference
    if "men" in query_lower or "man" in query_lower:
        intent.gender_preference = "male"
    elif "women" in query_lower or "woman" in query_lower or "lady" in query_lower:
        intent.gender_preference = "female"

    return intent

def perform_web_search(intent: IntentSchema) -> List[str]:
    """Stub search that returns search-evidence statements based on keywords."""
    search_query = f"{intent.celebrity_name or ''} {intent.movie_name or ''} sunglasses".strip()
    print(f"NLUnderstandingTool: Querying Brave/Tavily for '{search_query}'...")
    
    # In a live app we make requests:
    # brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
    # response = requests.get("https://api.search.brave.com/...", headers={"X-Subscription-Token": brave_key})
    
    # Static responses for common demo queries:
    if "Daniel Craig" in search_query:
        return [
            "In Skyfall (2012), Daniel Craig plays James Bond wearing Tom Ford Snowdon FT0237 sunglasses.",
            "The Tom Ford Snowdon features a shiny black acetate square frame with vintage style details.",
            "Expert analysis confirms Bond's glasses have dark gray lenses."
        ]
    elif "Robert Downey" in search_query or "Iron Man" in search_query:
        return [
            "Tony Stark wears Matsuda M3079 sunglasses in Iron Man 3, featuring a round double-bridge metal frame.",
            "The sunglasses feature a custom red or gold mirror tint lens with side shields.",
            "Popular styles associated with Robert Downey Jr. include metal luxury round double-bar frames."
        ]
        
    return [f"General search results matching custom inquiry: {search_query}"]

def enrich_intent_from_evidence(intent: IntentSchema, evidence: List[str]):
    """Refines intent properties based on strings found in gathered search summaries."""
    combined_ev = " ".join(evidence).lower()
    
    if "square" in combined_ev:
        intent.shape_preference = "square"
    elif "round" in combined_ev:
        intent.shape_preference = "round"
        
    if "black" in combined_ev:
        intent.color_preference = "black"
    elif "gold" in combined_ev:
        intent.color_preference = "gold"

    if "acetate" in combined_ev:
        intent.style_descriptors.append("classic")
    if "metal" in combined_ev:
        intent.style_descriptors.append("luxury")
