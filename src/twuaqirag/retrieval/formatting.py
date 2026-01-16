from langchain_core.documents import Document

def docs_to_context(docs: list[Document], max_chars: int = 6000) -> str:

    parts = []
    total = 0

    for i, doc in enumerate(docs, start=1):
        meta = doc.metadata or {}
        
        meta_str = ",".join(
             f"{k}={meta[k]}"
             for k in ["place_id", "name", "name_ar", "floor", "building", "corridor", "category", "lang"]
             if k in meta and meta[k] is not None
        )

        chunk = doc.page_content.strip()
        block = f"[Doc {i}: {meta_str}]\n\n{chunk}"

        if total + len(block) > max_chars:
            break
    
        parts.append(block)
        total += len(block)

    return "\n\n".join(parts) if parts else ""