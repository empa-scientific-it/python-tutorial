import typing as t
from collections import OrderedDict

import Levenshtein as Lev
import tiktoken as tk
from datasketch import MinHash, MinHashLSH


class FuzzyCache:
    """A cache for fuzzy matching of strings based on MinHash and Levenshtein distance."""

    def __init__(self, threshold=0.8, n_permutations=128, cache_size=50) -> None:
        self.threshold = threshold
        self.n_permutations = n_permutations
        self.lsh = MinHashLSH(threshold=threshold, num_perm=n_permutations)
        self._encoder = tk.encoding_for_model("gpt-4o-mini")
        self._cache_size = cache_size
        self._cache = OrderedDict()

    def _encode(self, text: str) -> t.Sequence[bytes]:
        """Encode a text into a sequence of byte tokens."""
        return [
            self._encoder.decode_single_token_bytes(token)
            for token in self._encoder.encode(text)
        ]

    def _generate_hash(self, text: str) -> MinHash:
        m = MinHash(num_perm=self.n_permutations)
        for token in self._encode(text):
            m.update(token)
        return m

    def _is_similar(self, text_1: str, text_2: str) -> bool:
        distance = Lev.distance(text_1, text_2)
        max_len = max(len(text_1), len(text_2))
        similarity = 1 - (distance / max_len)
        return similarity >= self.threshold

    def _cache_response(self, query: str, response: t.Any) -> None:
        m = self._generate_hash(query)
        self.lsh.insert(query, m)
        self._cache[query] = response
        self._evict_cache()

    def _evict_cache(self) -> None:
        """Evict the least recently used item from the cache."""
        if len(self._cache) > self._cache_size:
            self._cache.popitem(last=False)  # FIFO

    def __getitem__(self, query: str) -> t.Optional[t.Any]:
        m = self._generate_hash(query)
        similar_keys = self.lsh.query(m)

        for key in similar_keys:
            cached_query = str(key)
            if self._is_similar(query, cached_query):
                self._cache.move_to_end(cached_query)
                return self._cache[cached_query]

        return None

    def __setitem__(self, query: str, response: t.Any) -> None:
        self._cache_response(query, response)
