"""
Resolve place / aliases / place_id
This module will handle place name resolution and alias management
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document

from .vector_store import get_retriever
from .formatting import docs_to_context

LangCode = Literal['ar' , 'en']

@dataclass
class RetrieverConfig:
    k_primery: int = 6
    k_fallback: int = 6
    min_docs: int =2
    max_chars: int = 6000


class RAGRetriever:
    def __init__(self, store: Chroma, config: Optional[RetrievalConfig] = None):
        self.store = store
        self.config = config or RetrievalConfig()

    def _is_weak(self, docs: list[Document]) -> bool:
        if len(docs) < self.config.min_docs:
            return True
        total_len = sum(len(d.page_content or "") for d in docs)
        return total_len < 250
    

    async def retrieve(self, query: str, response_lang: LangCode) -> str:
            """
        Returns context string. Uses language filter + fallback strategies.
        """
        # 1) Primary: lang-filtered
            r1 = get_retriever(self.store, lang=response_lang, k=self.config.k_primary)
            docs1 = r1.invoke(query)
            if not self._is_weak(docs1):
                return docs_to_context(docs1, max_chars=self.config.max_chars)

            # 2) Fallback: no lang filter
            r2 = get_retriever(self.store, lang=None, k=self.config.k_fallback)
            docs2 = r2.invoke(query)
            if not self._is_weak(docs2):
                return docs_to_context(docs2, max_chars=self.config.max_chars)

            # 3) Dual: search both languages and merge
            r_ar = get_retriever(self.store, lang="ar", k=self.config.k_fallback)
            r_en = get_retriever(self.store, lang="en", k=self.config.k_fallback)
            docs_ar = r_ar.invoke(query)
            docs_en = r_en.invoke(query)

            merged = self._merge_unique(docs1 + docs2 + docs_ar + docs_en)
            return docs_to_context(merged, max_chars=self.config.max_chars)  

    def _merge_unique(self, docs: list[Document])   -> list[Document]:

        seen = set()
        out = []

        for d in docs:
            key = (d.page_content[:80], tuple(sorted((d.metadata or {}).items())))
            if key in seen:
                continue
            seen.add(key)
            out.append(d)
        return out