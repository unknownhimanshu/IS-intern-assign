from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np


def simhash(text: str) -> int:
    words = text.lower().split()
    shingles = [" ".join(words[i:i + 4]) for i in range(max(1, len(words) - 3))]
    bits = [0] * 64
    for shingle in shingles:
        value = int.from_bytes(hashlib.blake2b(shingle.encode(), digest_size=8).digest(), "big")
        for bit in range(64):
            bits[bit] += 1 if value >> bit & 1 else -1
    return sum((1 << i) for i, value in enumerate(bits) if value > 0)


def hamming(left: int, right: int) -> int:
    return (left ^ right).bit_count()


@dataclass(frozen=True, slots=True)
class DedupResult:
    kept: list[int]
    dropped: list[tuple[int, int, str]]


def dedupe(texts: list[str], embeddings: np.ndarray, cosine_threshold: float = .93) -> DedupResult:
    normalized = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-9)
    hashes = [simhash(text) for text in texts]
    kept: list[int] = []
    dropped: list[tuple[int, int, str]] = []
    for index in range(len(texts)):
        duplicate: tuple[int, str] | None = None
        for prior in kept:
            if hamming(hashes[index], hashes[prior]) <= 3:
                duplicate = (prior, "simhash")
                break
            if float(normalized[index] @ normalized[prior]) >= cosine_threshold:
                duplicate = (prior, "cosine")
                break
        if duplicate:
            dropped.append((index, duplicate[0], duplicate[1]))
        else:
            kept.append(index)
    return DedupResult(kept, dropped)
