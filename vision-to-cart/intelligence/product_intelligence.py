import os
import math
from typing import List, Dict, Any, Optional

# Attempt to import sentence-transformers for local embeddings
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    print("ProductIntelligence: sentence-transformers model loaded successfully.")
except Exception as e:
    print(f"ProductIntelligence: sentence-transformers not available ({e}). Using simulated word-match embeddings.")
    EMBEDDING_MODEL = None

# Attempt to import chromadb
try:
    import chromadb
    CHROMA_CLIENT = None
except Exception as e:
    print(f"ProductIntelligence: chromadb not available ({e}). Using local memory collection fallback.")
    chromadb = None


class ProductIntelligence:
    def __init__(self, db_path: str = "data_services/vector_store"):
        self.db_path = db_path
        self.in_memory_collection: List[Dict[str, Any]] = []
        self._init_db()

    def _init_db(self):
        global CHROMA_CLIENT
        if chromadb:
            try:
                os.makedirs(self.db_path, exist_ok=True)
                CHROMA_CLIENT = chromadb.PersistentClient(path=self.db_path)
            except Exception as e:
                print(f"ChromaDB initialization failed: {e}. Falling back to in-memory store.")
                CHROMA_CLIENT = None
        else:
            CHROMA_CLIENT = None

        # Automatically load enriched catalog for the in-memory fallback
        if not self.in_memory_collection:
            enriched_path = os.getenv("ENRICHED_CATALOG_PATH", "data_services/catalog/catalog_enriched.json")
            if not os.path.exists(enriched_path):
                enriched_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data_services", "catalog", "catalog_enriched.json")
            
            if os.path.exists(enriched_path):
                try:
                    import json
                    with open(enriched_path, "r", encoding="utf-8") as f:
                        products = json.load(f)
                    
                    self.in_memory_collection = []
                    for p in products:
                        search_text = self.build_product_search_text(p)
                        vector = self.get_embedding(search_text)
                        self.in_memory_collection.append({
                            "product_id": p.get("product_id"),
                            "metadata": p,
                            "search_text": search_text,
                            "vector": vector
                        })
                    print(f"ProductIntelligence: Pre-loaded {len(self.in_memory_collection)} products from catalog cache.")
                except Exception as e:
                    print(f"ProductIntelligence: Error pre-loading catalog cache: {e}")

    def get_embedding(self, text: str) -> List[float]:
        """Generates a list of floats (embedding vector) for the given text."""
        if EMBEDDING_MODEL:
            try:
                vector = EMBEDDING_MODEL.encode(text)
                return vector.tolist()
            except Exception as e:
                print(f"Error encoding embedding: {e}")
                
        # Word frequency-based simple hashing fallback to produce a consistent 384-dim vector
        vector = [0.0] * 384
        words = text.lower().split()
        for i, word in enumerate(words):
            hash_val = hash(word) % 384
            vector[hash_val] += 1.0
            
        # Normalize the vector
        magnitude = math.sqrt(sum(v*v for v in vector))
        if magnitude > 0:
            vector = [v / magnitude for v in vector]
        return vector

    def build_product_search_text(self, p: Dict[str, Any]) -> str:
        """Constructs a descriptive text string from product attributes to embed."""
        tags_str = ", ".join(p.get("style_tags", []))
        desc = (
            f"A pair of {p.get('gender', 'unisex')} {p.get('frame_material', '')} "
            f"{p.get('frame_color', '')} {p.get('shape', '')} sunglasses or glasses "
            f"with {p.get('lens_color', '')} lenses. Brand is {p.get('brand', 'generic')}. "
            f"Style is characterized as {tags_str}."
        )
        return desc

    def ingest_catalog(self, products: List[Dict[str, Any]]) -> bool:
        """Ingests enriched catalog items into ChromaDB or local cache."""
        self.in_memory_collection = []
        
        # Populate in-memory collection first (will serve as fallback)
        for p in products:
            search_text = self.build_product_search_text(p)
            vector = self.get_embedding(search_text)
            self.in_memory_collection.append({
                "product_id": p.get("product_id"),
                "metadata": p,
                "search_text": search_text,
                "vector": vector
            })

        # Try to ingest to ChromaDB
        if chromadb and CHROMA_CLIENT:
            try:
                collection = CHROMA_CLIENT.get_or_create_collection(
                    name="vision_to_cart_catalog",
                    metadata={"hnsw:space": "cosine"}
                )
                
                ids = [p["product_id"] for p in self.in_memory_collection]
                embeddings = [p["vector"] for p in self.in_memory_collection]
                metadatas = []
                for p in self.in_memory_collection:
                    # Flatten lists for metadata compatibility (ChromaDB does not support list fields easily)
                    meta = p["metadata"].copy()
                    meta["style_tags"] = ",".join(meta.get("style_tags", []))
                    metadatas.append(meta)
                documents = [p["search_text"] for p in self.in_memory_collection]
                
                collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=documents
                )
                print(f"ProductIntelligence: Ingested {len(ids)} products into ChromaDB.")
                return True
            except Exception as e:
                print(f"Error writing to ChromaDB: {e}. Keeping in-memory fallback store.")
                
        print(f"ProductIntelligence: Kept {len(self.in_memory_collection)} products in-memory.")
        return True

    def query_vector_search(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Queries the vector database (or local memory) and returns nearest matches."""
        query_vector = self.get_embedding(query_text)
        
        # Check if ChromaDB is available
        if chromadb and CHROMA_CLIENT:
            try:
                collection = CHROMA_CLIENT.get_collection(name="vision_to_cart_catalog")
                results = collection.query(
                    query_embeddings=[query_vector],
                    n_results=top_k
                )
                
                candidates = []
                if results and "metadatas" in results and results["metadatas"]:
                    for i in range(len(results["ids"][0])):
                        meta = results["metadatas"][0][i].copy()
                        # Unflatten style_tags back to list
                        if "style_tags" in meta and isinstance(meta["style_tags"], str):
                            meta["style_tags"] = meta["style_tags"].split(",") if meta["style_tags"] else []
                        
                        # Calculate distance score (ChromaDB returns distance, we want similarity 0-1)
                        dist = results["distances"][0][i] if "distances" in results else 0.5
                        similarity = 1.0 - (dist / 2.0) if dist <= 2.0 else 0.0 # Standardize cosine distance mapping
                        
                        candidates.append({
                            "product": meta,
                            "vector_score": similarity
                        })
                return candidates
            except Exception as e:
                print(f"ChromaDB search failed: {e}. Falling back to in-memory cosine query.")

        # In-memory cosine similarity fallback
        candidates = []
        for item in self.in_memory_collection:
            # Cosine similarity between query_vector and item["vector"]
            item_vec = item["vector"]
            dot_product = sum(q*i for q, i in zip(query_vector, item_vec))
            q_magnitude = math.sqrt(sum(q*q for q in query_vector))
            i_magnitude = math.sqrt(sum(i*i for i in item_vec))
            
            similarity = 0.0
            if q_magnitude > 0 and i_magnitude > 0:
                similarity = dot_product / (q_magnitude * i_magnitude)
                
            candidates.append({
                "product": item["metadata"],
                "vector_score": similarity
            })
            
        # Sort by similarity descending
        candidates.sort(key=lambda x: x["vector_score"], reverse=True)
        return candidates[:top_k]
