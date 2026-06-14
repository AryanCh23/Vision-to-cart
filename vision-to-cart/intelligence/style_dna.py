from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class StyleDNA:
    shape: Optional[str] = None
    frame_color: Optional[str] = None
    lens_color: Optional[str] = None
    frame_material: Optional[str] = None
    gender: Optional[str] = "unisex"
    style_tags: List[str] = field(default_factory=list)
    brand_hint: Optional[str] = None
    price_range_preference: Optional[str] = None # e.g., "budget", "mid", "premium"
    confidence_score: float = 0.0
    source: str = "nl"  # "image", "nl", "web"

    def to_search_text(self) -> str:
        """
        Converts the StyleDNA attributes into a descriptive natural-language sentence
        suitable for embedding generation and semantic similarity search.
        """
        clauses = []
        
        # Gender context
        if self.gender and self.gender != "unisex":
            clauses.append(f"{self.gender}'s")
            
        # Material, color, and shape description
        desc_parts = []
        if self.frame_material:
            desc_parts.append(self.frame_material)
        if self.frame_color:
            desc_parts.append(self.frame_color)
        
        desc = " ".join(desc_parts)
        if self.shape:
            desc = f"{desc} {self.shape} sunglasses" if desc else f"{self.shape} sunglasses"
        else:
            desc = f"{desc} glasses" if desc else "eyewear sunglasses"
            
        clauses.append(desc)
        
        if self.lens_color:
            clauses.append(f"with {self.lens_color} lenses")
            
        if self.brand_hint:
            clauses.append(f"by {self.brand_hint}")
            
        if self.style_tags:
            tags_str = ", ".join(self.style_tags)
            clauses.append(f"featuring a {tags_str} style")
            
        if self.price_range_preference:
            clauses.append(f"in the {self.price_range_preference} price tier")

        return " ".join(clauses)
