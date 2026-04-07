"""
Embedding Engine — FAISS-based vector store for SHL assessments.

Uses sentence-transformers to generate embeddings and FAISS for
fast similarity search.
"""

import json
import os
import pickle
from typing import Dict, List, Optional, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


class EmbeddingEngine:
    """Manages embedding generation and FAISS vector index."""
    
    MODEL_NAME = "all-MiniLM-L6-v2"
    
    def __init__(
        self,
        index_path: str = "data/faiss_index.bin",
        metadata_path: str = "data/faiss_metadata.json",
    ):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.IndexFlatIP] = None
        self.metadata: List[Dict] = []
    
    def _load_model(self):
        """Lazy-load the sentence transformer model."""
        if self.model is None:
            print(f"Loading embedding model: {self.MODEL_NAME}")
            self.model = SentenceTransformer(self.MODEL_NAME)
            print("Model loaded successfully")
    
    def _build_document_text(self, assessment: Dict) -> str:
        """
        Combine assessment fields into a single text for embedding.
        Combines: name + description + test_type for rich semantic representation.
        """
        name = assessment.get("name", "")
        description = assessment.get("description", "")
        test_types = assessment.get("test_type", [])
        
        if isinstance(test_types, list):
            test_type_str = ", ".join(test_types)
        else:
            test_type_str = str(test_types)
        
        # Build combined text
        parts = [name]
        if description and description != "Description unavailable":
            parts.append(description)
        if test_type_str and test_type_str != "Unknown":
            parts.append(f"Test type: {test_type_str}")
        
        return " | ".join(parts)
    
    def build_index(self, data_path: str = "data/scraped_data.json") -> None:
        """
        Build FAISS index from scraped assessment data.
        
        Args:
            data_path: Path to the JSON file containing scraped assessments.
        """
        self._load_model()
        
        # Load assessment data
        with open(data_path, "r", encoding="utf-8") as f:
            assessments = json.load(f)
        
        print(f"Building index from {len(assessments)} assessments...")
        
        # Build document texts
        documents = []
        valid_assessments = []
        
        for assessment in assessments:
            doc_text = self._build_document_text(assessment)
            if doc_text.strip():
                documents.append(doc_text)
                valid_assessments.append(assessment)
        
        print(f"Generating embeddings for {len(documents)} documents...")
        
        # Generate embeddings
        embeddings = self.model.encode(
            documents,
            show_progress_bar=True,
            normalize_embeddings=True,  # Normalize for cosine similarity via inner product
            batch_size=32,
        )
        
        embeddings_np = np.array(embeddings, dtype=np.float32)
        
        # Build FAISS index (Inner Product = cosine similarity when normalized)
        dimension = embeddings_np.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings_np)
        
        # Store metadata
        self.metadata = valid_assessments
        
        # Persist to disk
        self._save_index()
        
        print(f"FAISS index built: {self.index.ntotal} vectors, dimension={dimension}")
        print(f"Index saved to {self.index_path}")
        print(f"Metadata saved to {self.metadata_path}")
    
    def _save_index(self) -> None:
        """Save index and metadata to disk."""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def load_index(self) -> bool:
        """
        Load pre-built index and metadata from disk.
        Returns True if loaded successfully, False otherwise.
        """
        if not os.path.exists(self.index_path) or not os.path.exists(self.metadata_path):
            print("Index files not found. Run build_index() first.")
            return False
        
        self.index = faiss.read_index(self.index_path)
        
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
        
        print(f"Loaded FAISS index: {self.index.ntotal} vectors")
        return True
    
    def encode_query(self, query: str) -> np.ndarray:
        """Encode a query string into an embedding vector."""
        self._load_model()
        embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )
        return np.array(embedding, dtype=np.float32)
    
    def search(self, query: str, top_k: int = 20) -> List[Tuple[Dict, float]]:
        """
        Search the index for the most similar assessments.
        
        Args:
            query: Search query string.
            top_k: Number of results to return.
            
        Returns:
            List of (assessment_dict, similarity_score) tuples.
        """
        if self.index is None:
            if not self.load_index():
                raise RuntimeError("No index available. Build or load one first.")
        
        query_embedding = self.encode_query(query)
        
        # Search FAISS
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata) and idx >= 0:
                results.append((self.metadata[idx], float(score)))
        
        return results


if __name__ == "__main__":
    engine = EmbeddingEngine()
    engine.build_index()
    
    # Test search
    test_query = "Java developer assessment for mid-level engineer"
    results = engine.search(test_query, top_k=5)
    print(f"\nTest query: '{test_query}'")
    for i, (assessment, score) in enumerate(results, 1):
        print(f"  {i}. [{score:.4f}] {assessment['name']}")
