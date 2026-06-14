import time
from typing import Dict, Any, List, Optional

class SessionState:
    def __init__(self, session_id: str):
        self.session_id: str = session_id
        self.last_style_dna: Optional[Dict[str, Any]] = None
        self.shown_product_ids: List[str] = []
        self.last_query: Optional[str] = None
        self.last_updated: float = time.time()

class ContextManager:
    """
    Manages session isolation and chat state history.
    Detects if the query contains refinement indicators (e.g., 'cheaper', 'similar')
    and synthesizes context.
    """
    _sessions: Dict[str, SessionState] = {}

    def get_session(self, session_id: str) -> SessionState:
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState(session_id)
        else:
            self._sessions[session_id].last_updated = time.time()
        return self._sessions[session_id]

    def save_style_dna(self, session_id: str, dna_dict: Dict[str, Any]):
        session = self.get_session(session_id)
        session.last_style_dna = dna_dict

    def save_shown_products(self, session_id: str, product_ids: List[str]):
        session = self.get_session(session_id)
        session.shown_product_ids = product_ids

    def merge_query_with_context(self, session_id: str, current_query: str) -> str:
        """
        Scans for conversational refinement signals. If found and previous context
        exists, combines the new intent instructions with the historical StyleDNA description.
        """
        session = self.get_session(session_id)
        if not session.last_style_dna:
            session.last_query = current_query
            return current_query

        # Refinement signals
        refinement_signals = [
            "cheaper", "less expensive", "more expensive", "premium", "budget",
            "similar", "same brand", "same frame", "different color", "show more",
            "other option", "alternatives"
        ]

        query_lower = current_query.lower()
        has_signal = any(signal in query_lower for signal in refinement_signals)

        if has_signal:
            dna = session.last_style_dna
            # Build a string describing the previous item style
            parts = []
            if dna.get("brand_hint"):
                parts.append(f"brand {dna['brand_hint']}")
            if dna.get("frame_color"):
                parts.append(f"{dna['frame_color']} frame")
            if dna.get("shape"):
                parts.append(f"{dna['shape']} shape")
            if dna.get("lens_color"):
                parts.append(f"{dna['lens_color']} lenses")
                
            context_str = ", ".join(parts)
            merged = f"{current_query} (context refinement based on previously viewed: {context_str})"
            session.last_query = merged
            return merged

        session.last_query = current_query
        return current_query
