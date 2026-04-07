"""
Retrieval Pipeline — Full RAG retrieval with hybrid search, re-ranking,
and balanced recommendations.

Pipeline:
  1. Query -> Embedding (FAISS semantic search)
  2. Query -> BM25 (keyword search)
  3. Hybrid fusion of results
  4. Re-ranking by combined score
  5. Balanced K/P selection
  6. Return top 5-10
"""

import json
import math
import os
import re
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from embeddings.embedding_engine import EmbeddingEngine


class RetrievalPipeline:
    """
    Full RAG retrieval pipeline with:
    - FAISS semantic search
    - BM25 keyword search (hybrid)
    - Score fusion and re-ranking
    - Balanced K (Knowledge) / P (Personality) recommendations
    """
    
    def __init__(
        self,
        data_path: str = "data/scraped_data.json",
        index_path: str = "data/faiss_index.bin",
        metadata_path: str = "data/faiss_metadata.json",
    ):
        self.data_path = data_path
        self.index_path = index_path
        self.metadata_path = metadata_path
        
        # Initialize embedding engine
        self.engine = EmbeddingEngine(
            index_path=index_path,
            metadata_path=metadata_path,
        )
        
        # BM25 index
        self.bm25: Optional[object] = None
        self.bm25_corpus: List[Dict] = []
        
        self._initialized = False
    
    def initialize(self) -> None:
        """Load or build all required indexes."""
        if self._initialized:
            return
        
        # Load or build FAISS index
        if not self.engine.load_index():
            print("Building FAISS index...")
            self.engine.build_index(self.data_path)
        
        # Build BM25 index
        self._build_bm25_index()
        
        self._initialized = True
        print("Retrieval pipeline initialized")
    
    def _build_bm25_index(self) -> None:
        """Build BM25 index from assessment data."""
        if BM25Okapi is None:
            print("Warning: rank_bm25 not installed. Hybrid search disabled.")
            return
        
        with open(self.data_path, "r", encoding="utf-8") as f:
            assessments = json.load(f)
        
        self.bm25_corpus = assessments
        
        # Tokenize documents for BM25
        tokenized_docs = []
        for item in assessments:
            text = self._build_bm25_text(item)
            tokens = self._tokenize(text)
            tokenized_docs.append(tokens)
        
        self.bm25 = BM25Okapi(tokenized_docs)
        print(f"BM25 index built with {len(tokenized_docs)} documents")
    
    def _build_bm25_text(self, assessment: Dict) -> str:
        """Build searchable text for BM25 from assessment data."""
        parts = [
            assessment.get("name", ""),
            assessment.get("description", ""),
        ]
        test_types = assessment.get("test_type", [])
        if isinstance(test_types, list):
            parts.extend(test_types)
        else:
            parts.append(str(test_types))
        return " ".join(parts)
    
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Simple tokenization for BM25."""
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        tokens = text.split()
        # Remove very short tokens
        return [t for t in tokens if len(t) > 1]
    
    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        initial_k: int = 20,
        balance_types: bool = True,
        semantic_weight: float = 0.7,
        bm25_weight: float = 0.3,
    ) -> List[Dict]:
        """
        Full retrieval pipeline.
        
        Args:
            query: Natural language query or job description.
            top_k: Final number of results (5-10).
            initial_k: Number of candidates to retrieve before re-ranking.
            balance_types: Whether to balance K and P test types.
            semantic_weight: Weight for semantic similarity score.
            bm25_weight: Weight for BM25 keyword score.
            
        Returns:
            List of assessment dictionaries with scores.
        """
        self.initialize()
        
        # Step 1: FAISS semantic search (top initial_k)
        semantic_results = self.engine.search(query, top_k=initial_k)
        
        # Step 2: BM25 keyword search (top initial_k)
        bm25_results = self._bm25_search(query, top_k=initial_k)
        
        # Step 3: Hybrid fusion
        fused = self._hybrid_fusion(
            semantic_results,
            bm25_results,
            semantic_weight=semantic_weight,
            bm25_weight=bm25_weight,
        )
        
        # Step 4: Re-rank by fused score
        fused.sort(key=lambda x: x[1], reverse=True)
        
        # Step 5: Balance K/P types if requested
        if balance_types:
            selected = self._balance_recommendations(fused, top_k)
        else:
            selected = fused[:top_k]
        
        # Step 6: Format output
        results = []
        for assessment, score in selected:
            result = dict(assessment)
            result["relevance_score"] = round(score, 4)
            results.append(result)
        
        return results
    
    def _bm25_search(self, query: str, top_k: int = 20) -> List[Tuple[Dict, float]]:
        """BM25 keyword search."""
        if self.bm25 is None:
            return []
        
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        
        scores = self.bm25.get_scores(query_tokens)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        max_score = max(scores) if max(scores) > 0 else 1.0
        
        for idx in top_indices:
            if scores[idx] > 0:
                normalized_score = scores[idx] / max_score
                results.append((self.bm25_corpus[idx], float(normalized_score)))
        
        return results
    
    def _hybrid_fusion(
        self,
        semantic_results: List[Tuple[Dict, float]],
        bm25_results: List[Tuple[Dict, float]],
        semantic_weight: float = 0.7,
        bm25_weight: float = 0.3,
    ) -> List[Tuple[Dict, float]]:
        """
        Fuse semantic and BM25 results using weighted Reciprocal Rank Fusion.
        """
        url_scores: Dict[str, float] = defaultdict(float)
        url_assessments: Dict[str, Dict] = {}
        
        # Add semantic scores
        for rank, (assessment, score) in enumerate(semantic_results):
            url = assessment.get("url", "")
            rrf_score = 1.0 / (rank + 60)  # RRF with k=60
            url_scores[url] += semantic_weight * (score + rrf_score)
            url_assessments[url] = assessment
        
        # Add BM25 scores
        for rank, (assessment, score) in enumerate(bm25_results):
            url = assessment.get("url", "")
            rrf_score = 1.0 / (rank + 60)
            url_scores[url] += bm25_weight * (score + rrf_score)
            if url not in url_assessments:
                url_assessments[url] = assessment
        
        # Combine into list
        fused = []
        for url, score in url_scores.items():
            if url in url_assessments:
                fused.append((url_assessments[url], score))
        
        return fused
    
    def _balance_recommendations(
        self,
        ranked_results: List[Tuple[Dict, float]],
        top_k: int = 10,
    ) -> List[Tuple[Dict, float]]:
        """
        Balance recommendations between Knowledge & Skills (K) 
        and Personality & Behavior (P) test types.
        
        Ensures a healthy mix of both cognitive/skills tests 
        and personality/behavioral assessments.
        """
        k_results = []  # Knowledge & Skills
        p_results = []  # Personality & Behavior
        other_results = []
        
        for assessment, score in ranked_results:
            test_types = assessment.get("test_type", [])
            if isinstance(test_types, str):
                test_types = [test_types]
            
            has_k = any("Knowledge" in t or "Skill" in t for t in test_types)
            has_p = any("Personality" in t or "Behavior" in t for t in test_types)
            
            if has_k and has_p:
                # Mixed type — add to both pools
                k_results.append((assessment, score))
                p_results.append((assessment, score))
            elif has_k:
                k_results.append((assessment, score))
            elif has_p:
                p_results.append((assessment, score))
            else:
                other_results.append((assessment, score))
        
        # Allocate slots: aim for ~60% K, ~30% P, ~10% other
        k_slots = max(2, int(top_k * 0.5))
        p_slots = max(1, int(top_k * 0.3))
        other_slots = top_k - k_slots - p_slots
        
        selected = []
        seen_urls = set()
        
        def add_unique(results, max_count):
            count = 0
            for assessment, score in results:
                url = assessment.get("url", "")
                if url not in seen_urls and count < max_count:
                    seen_urls.add(url)
                    selected.append((assessment, score))
                    count += 1
        
        add_unique(k_results, k_slots)
        add_unique(p_results, p_slots)
        add_unique(other_results, other_slots)
        
        # Fill remaining slots from ranked results
        remaining = top_k - len(selected)
        if remaining > 0:
            for assessment, score in ranked_results:
                url = assessment.get("url", "")
                if url not in seen_urls and remaining > 0:
                    seen_urls.add(url)
                    selected.append((assessment, score))
                    remaining -= 1
        
        # Sort by score
        selected.sort(key=lambda x: x[1], reverse=True)
        
        return selected[:top_k]
    
    def retrieve_urls(self, query: str, top_k: int = 10) -> List[str]:
        """Retrieve only URLs for evaluation purposes."""
        results = self.retrieve(query, top_k=top_k, balance_types=False)
        return [r["url"] for r in results]


if __name__ == "__main__":
    pipeline = RetrievalPipeline()
    
    test_query = "I need a test for hiring Java developers at mid-level"
    print(f"\nQuery: '{test_query}'")
    print("-" * 60)
    
    results = pipeline.retrieve(test_query, top_k=10)
    for i, result in enumerate(results, 1):
        print(f"{i}. [{result['relevance_score']:.4f}] {result['name']}")
        print(f"   Type: {result.get('test_type', [])}")
        print(f"   URL: {result['url']}")
