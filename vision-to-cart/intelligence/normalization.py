from typing import List, Dict, Any, Optional

# Shape Normalization Map
SHAPE_MAP: Dict[str, str] = {
    "aviators": "aviator",
    "aviator": "aviator",
    "teardrop": "aviator",
    "roundish": "round",
    "round": "round",
    "circular": "round",
    "rectangle": "rectangle",
    "rectangular": "rectangle",
    "cat-eye": "cat-eye",
    "cateye": "cat-eye",
    "butterfly": "cat-eye",
    "oval": "oval",
    "ovalish": "oval",
    "sporty": "sport",
    "sport": "sport",
    "wrap-around": "sport",
    "shield": "sport",
    "square": "square",
    "squarish": "square",
    "oversized": "square"  # default oversized to square or match catalog
}

# Color Normalization Map
COLOR_MAP: Dict[str, str] = {
    "golden": "gold",
    "gold": "gold",
    "rose-gold": "gold",
    "rose gold": "gold",
    "silvery": "silver",
    "silver": "silver",
    "chrome": "silver",
    "dark black": "black",
    "black": "black",
    "stealth": "black",
    "charcoal": "black",
    "brownish": "brown",
    "brown": "brown",
    "tortoise": "brown",
    "tortoiseshell": "brown",
    "clear": "clear",
    "transparent": "clear",
    "pink": "pink",
    "pinkish": "pink",
    "blue": "blue",
    "bluish": "blue",
    "green": "green",
    "greenish": "green",
    "gray": "gray",
    "grey": "gray",
    "red": "red",
    "mirror": "mirror",
    "mirrored": "mirror",
    "yellow": "yellow"
}

# Material Normalization Map
MATERIAL_MAP: Dict[str, str] = {
    "metallic": "metal",
    "metal": "metal",
    "wire": "metal",
    "plastic": "acetate",
    "acetate": "acetate",
    "shell": "acetate",
    "wood": "wooden",
    "wooden": "wooden",
    "wood-grain": "wooden",
    "titanium": "titanium"
}

# Style Tags Normalization Map
STYLE_MAP: Dict[str, str] = {
    "luxury": "luxury",
    "luxurious": "luxury",
    "prestige": "luxury",
    "casual": "casual",
    "everyday": "casual",
    "sporty": "sporty",
    "sport": "sporty",
    "active": "sporty",
    "performance": "sporty",
    "classic": "classic",
    "vintage": "classic",
    "retro": "classic",
    "trendy": "trendy",
    "fashion-forward": "trendy",
    "bold": "trendy",
    "minimalist": "minimalist",
    "clean": "minimalist"
}

def normalize_attribute(category: str, value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    val = value.strip().lower()
    
    if category == "shape":
        return SHAPE_MAP.get(val, val)
    elif category == "color":
        return COLOR_MAP.get(val, val)
    elif category == "material":
        return MATERIAL_MAP.get(val, val)
    elif category == "style":
        return STYLE_MAP.get(val, val)
        
    return val

def normalize_style_tags(tags: List[str]) -> List[str]:
    normalized = set()
    for tag in tags:
        norm = normalize_attribute("style", tag)
        if norm:
            normalized.add(norm)
    return list(normalized)
