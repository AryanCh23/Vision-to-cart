try:
    from pydantic import BaseModel, Field
except ImportError:
    class Field:
        def __init__(self, default=None, default_factory=None, description=""):
            self.default = default
            self.default_factory = default_factory
            self.description = description

    class BaseModel:
        def __init__(self, **data):
            for field_name in getattr(self, '__annotations__', {}).keys():
                default_val = None
                if hasattr(self.__class__, field_name):
                    val = getattr(self.__class__, field_name)
                    if isinstance(val, Field):
                        default_val = val.default if val.default is not None else (val.default_factory() if val.default_factory else None)
                    else:
                        default_val = val
                setattr(self, field_name, data.get(field_name, default_val))

        def dict(self):
            return {k: getattr(self, k) for k in getattr(self, '__annotations__', {}).keys()}

from typing import List, Optional, Dict, Any

class IntentSchema(BaseModel):
    celebrity_name: Optional[str] = Field(None, description="Actor, actress, or public figure referenced in query")
    movie_name: Optional[str] = Field(None, description="Movie, series, or video media referenced")
    event_name: Optional[str] = Field(None, description="Event or show, e.g., Oscars, Cannes Film Festival")
    product_type: Optional[str] = Field("sunglasses", description="Eyewear type, e.g., sunglasses, eyeglasses, frames")
    style_descriptors: List[str] = Field(default_factory=list, description="Styles like retro, classic, bold, sporty, oversized")
    gender_preference: Optional[str] = Field("unisex", description="Target gender: male, female, unisex")
    color_preference: Optional[str] = Field(None, description="Requested lens or frame color")
    shape_preference: Optional[str] = Field(None, description="Requested frame shape")
    brand_hint: Optional[str] = Field(None, description="Target brand, e.g., Ray-Ban, Gucci")
    price_refinement: Optional[str] = Field(None, description="Price filters like cheaper, more expensive, budget, premium")
    comparative_product_id: Optional[str] = Field(None, description="Referenced product for comparison, e.g., similar to P001")

    def dict_summary(self) -> Dict[str, Any]:
        """Returns non-empty keys only for simple printing."""
        return {k: v for k, v in self.dict().items() if v is not None and v != []}
