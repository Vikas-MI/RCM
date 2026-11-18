"""Tiny local vector store — no OpenAI / Chroma required.

ELI5: Turn each policy paragraph into a bag of word scores. When you ask a
question, score how similar each paragraph is, and pick the top ones.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any


_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


class LocalVectorStore:
    def __init__(self, chunks: list[dict[str, Any]]):
        self.chunks = chunks
        self._docs = [tokenize(f"{c.get('title', '')} {c.get('text', '')}") for c in chunks]
        self._df: Counter[str] = Counter()
        for tokens in self._docs:
            for t in set(tokens):
                self._df[t] += 1
        self._n = max(len(chunks), 1)
        self._vectors = [self._tfidf(tokens) for tokens in self._docs]

    def _tfidf(self, tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        length = max(sum(tf.values()), 1)
        vec: dict[str, float] = {}
        for term, count in tf.items():
            idf = math.log((1 + self._n) / (1 + self._df[term])) + 1.0
            vec[term] = (count / length) * idf
        return vec

    @staticmethod
    def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        keys = set(a) & set(b)
        dot = sum(a[k] * b[k] for k in keys)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        qvec = self._tfidf(tokenize(query))
        scored = []
        for chunk, vec in zip(self.chunks, self._vectors):
            score = self._cosine(qvec, vec)
            scored.append({**chunk, "score": round(score, 4)})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
