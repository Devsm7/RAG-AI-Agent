from __future__ import annotations

from typing import Literal , Optional
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

LangCode = Literal['ar' , 'en']

CHROMA_DIR = 'chroma_db'
COLLECTION_NAME = 'twuiqiraq'

_embeddings = OllamaEmbeddings(model='mxbai-embed-large')

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=CHROMA_DIR,
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
