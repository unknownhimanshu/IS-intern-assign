from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import numpy as np
from rank_bm25 import BM25Okapi


@dataclass(frozen=True, slots=True)
class Chunk:
    id: str
    doc_id: str
    text: str
    section: str = ""


class HybridIndex:
    def __init__(self, chunks: list[Chunk], embeddings: np.ndarray) -> None:
        if len(chunks) != embeddings.shape[0]:
            raise ValueError("chunks and embeddings must be aligned")
        self.chunks = chunks
        self.embeddings = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-9)
        self.bm25 = BM25Okapi([chunk.text.lower().split() for chunk in chunks])

    def search(self, query: str, query_embedding: np.ndarray, top_k: int = 40) -> list[Chunk]:
        lexical = np.argsort(-self.bm25.get_scores(query.lower().split()))[:top_k * 2]
        vector = query_embedding / (np.linalg.norm(query_embedding) + 1e-9)
        dense = np.argsort(-(self.embeddings @ vector))[:top_k * 2]
        fused: dict[int, float] = defaultdict(float)
        for rank, index in enumerate(lexical):
            fused[int(index)] += 1 / (60 + rank + 1)
        for rank, index in enumerate(dense):
            fused[int(index)] += 1 / (60 + rank + 1)
        return [self.chunks[index] for index, _ in sorted(fused.items(), key=lambda item: -item[1])[:top_k]]


def mmr(candidate_embeddings: np.ndarray, query_embedding: np.ndarray, k: int, lambda_: float = .7) -> list[int]:
    candidates = candidate_embeddings / (np.linalg.norm(candidate_embeddings, axis=1, keepdims=True) + 1e-9)
    query = query_embedding / (np.linalg.norm(query_embedding) + 1e-9)
    relevance = candidates @ query
    selected: list[int] = []
    remaining = list(range(len(candidates)))
    while remaining and len(selected) < k:
        if not selected:
            best = max(remaining, key=lambda index: relevance[index])
        else:
            best = max(remaining, key=lambda index: lambda_ * relevance[index] - (1 - lambda_) * max(candidates[index] @ candidates[j] for j in selected))
        selected.append(best)
        remaining.remove(best)
    return selected
