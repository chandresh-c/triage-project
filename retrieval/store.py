"""
Policy Document Retrieval Subsystem: Hybrid Vector Store.

Combines token-frequency vector cosine similarity with BM25 keyword matching
to retrieve relevant insurance policy clauses without requiring external vector DB services.
"""

from typing import List, Dict, Any, Optional
import math
import re
from retrieval.policies import STANDARD_AUTO_POLICY_CLAUSES


def _tokenize(text: str) -> List[str]:
    """Tokenize and normalize text into lowercase alphanumeric tokens."""
    return re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())


class PolicyVectorStore:
    """
    In-memory hybrid retrieval engine simulating Azure AI Search.
    
    Combines:
    1. Lexical BM25 ranking for exact domain terminology (e.g. 'racing', 'deductible', 'rideshare').
    2. Vector cosine similarity over term frequencies for dense semantic matching.
    """

    def __init__(self, clauses: Optional[List[Dict[str, Any]]] = None):
        self.clauses: List[Dict[str, Any]] = clauses or list(STANDARD_AUTO_POLICY_CLAUSES)
        self._doc_tokens: List[List[str]] = [_tokenize(c["title"] + " " + c["text"]) for c in self.clauses]
        self._corpus_size: int = len(self.clauses)
        self._avg_doc_len: float = (
            sum(len(d) for d in self._doc_tokens) / self._corpus_size if self._corpus_size > 0 else 1.0
        )
        # Compute Document Frequencies
        self._df: Dict[str, int] = {}
        for doc in self._doc_tokens:
            for term in set(doc):
                self._df[term] = self._df.get(term, 0) + 1

    def _bm25_score(self, query_tokens: List[str], doc_idx: int, k1: float = 1.5, b: float = 0.75) -> float:
        doc = self._doc_tokens[doc_idx]
        doc_len = len(doc)
        score = 0.0

        for term in query_tokens:
            if term not in self._df:
                continue
            tf = doc.count(term)
            if tf == 0:
                continue
            # Standard BM25 IDF
            df = self._df[term]
            idf = math.log((self._corpus_size - df + 0.5) / (df + 0.5) + 1.0)
            # BM25 TF weight
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_len / self._avg_doc_len))
            score += idf * (numerator / denominator)

        return score

    def _cosine_score(self, query_tokens: List[str], doc_idx: int) -> float:
        doc = self._doc_tokens[doc_idx]
        query_set = set(query_tokens)
        doc_set = set(doc)
        intersection = query_set.intersection(doc_set)
        if not intersection:
            return 0.0
        # Overlap similarity
        return len(intersection) / (math.sqrt(len(query_set)) * math.sqrt(len(doc_set)))

    def search(self, query: str, top_k: int = 3, min_score: float = 0.05) -> List[Dict[str, Any]]:
        """
        Execute hybrid search over policy clauses.
        
        Args:
            query: Incident description, claim narrative, or coverage question.
            top_k: Number of highest-ranking clauses to return.
            min_score: Minimum relevance threshold.
            
        Returns:
            List of matching policy clauses with relevance scores.
        """
        query_tokens = _tokenize(query)
        if not query_tokens:
            return self.clauses[:top_k]

        scored_results = []
        for i, clause in enumerate(self.clauses):
            bm25 = self._bm25_score(query_tokens, i)
            cosine = self._cosine_score(query_tokens, i)
            # Hybrid fusion (BM25 weighted with cosine semantic overlap)
            hybrid_score = (0.7 * bm25) + (0.3 * (cosine * 10.0))
            if hybrid_score >= min_score or cosine > 0.1:
                scored_results.append({
                    "clause_id": clause["clause_id"],
                    "title": clause["title"],
                    "category": clause["category"],
                    "text": clause["text"],
                    "relevance_score": round(hybrid_score, 4)
                })

        scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_results[:top_k]
