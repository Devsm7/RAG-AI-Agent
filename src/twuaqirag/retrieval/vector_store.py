from __future__ import annotations

from typing import Literal , Optional
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from twuaqirag.core.config import config

LangCode = Literal['ar' , 'en']

_embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL)

vector_store = Chroma(
    collection_name='twuiqiraq',
    persist_directory=str(config.CHROMA_DB_DIR),
    embedding_function=_embeddings,
    )

def get_retriever(
    store: Chroma,
    lang: Optional[LangCode] = None,
    k: int = 20  # Increased to retrieve more documents
):
   search_kwargs= {'k': k}
   if lang:
      search_kwargs['filter'] = {'lang': lang}

   return store.as_retriever(search_kwargs=search_kwargs)
