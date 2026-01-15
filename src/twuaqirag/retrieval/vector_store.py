"""
Chroma init + retriever wrapper (migrated from vector.py)
Vector Search database using ChromaDB for local storage
"""
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd


# Load both CSV files
bootcamps_df = pd.read_csv(r"datasets\bootcamps_db.csv")
places_df = pd.read_csv(r"datasets\places_db.csv")

# Merge bootcamps with places data on place_id
merged_df = bootcamps_df.merge(places_df, left_on='place_id', right_on='id', suffixes=('_bootcamp', '_place'))

# Initialize Ollama embeddings
embeddings = OllamaEmbeddings(
    model="mxbai-embed-large",
)

db_location = "./chroma_db"

add_documents = not os.path.exists(db_location)


# Helper to generate content
def generate_content(row, lang="en"):
    if lang == "ar":
        return (
            f"المعسكر: {row.get('name_ar_bootcamp', row['name_bootcamp'])}, "
            f"عدد الطلاب: {row['number_of_students']}, "
            f"الوقت: من {row['start_time']} إلى {row['end_time']}, "
            f"الموقع: {row.get('name_ar_place', row['name_place'])}, "
            f"الفئة: {row.get('category_ar', row['category'])}, "
            f"الطابق: {row['floor']}, "
            f"الممر: {row['corridor']}"
        )

    # English (default)
    return (
        f"Bootcamp: {row['name_bootcamp']}, "
        f"Students: {row['number_of_students']}, "
        f"Time: {row['start_time']} to {row['end_time']}, "
        f"Location: {row['name_place']}, "
        f"Category: {row['category']}, "
        f"Floor: {row['floor']}, "
        f"Corridor: {row['corridor']}"
    )


# Helper to generate place content
def generate_place_content(row, lang="en"):
    if lang == "ar":
        return (
            f"المكان: {row.get('name_ar', row['name'])}, "
            f"الفئة: {row.get('category_ar', row['category'])}, "
            f"الطابق: {row['floor']}, "
            f"الممر: {row['corridor']}"
        )

    # English (default)
    return (
        f"Place: {row['name']}, "
        f"Category: {row['category']}, "
        f"Floor: {row['floor']}, "
        f"Corridor: {row['corridor']}"
    )


if add_documents:
    documents = []
    ids = []
    
    # First, add merged bootcamp + place documents
    for i, row in merged_df.iterrows():
        # 1. English Document
        content_en = generate_content(row, "en")
        doc_en = Document(
            page_content=content_en,
            id=f"bootcamp_{i}_en",
            metadata={
                "type": "bootcamp",
                "lang": "en",
                "bootcamp_name": row['name_bootcamp'],
                "bootcamp_name_ar": row.get('name_ar_bootcamp', ''),
                "students": row['number_of_students'],
                "start_time": str(row['start_time']),
                "end_time": str(row['end_time']),
                "place_name": row['name_place'],
                "place_name_ar": row.get('name_ar_place', ''),
                "category": row['category'],
                "category_ar": row.get('category_ar', ''),
                "floor": row['floor'],
                "corridor": row['corridor']
            }
        )
        ids.append(f"bootcamp_{i}_en")
        documents.append(doc_en)

        # 2. Arabic Document
        content_ar = generate_content(row, "ar")
        doc_ar = Document(
            page_content=content_ar,
            id=f"bootcamp_{i}_ar",
            metadata={
                "type": "bootcamp",
                "lang": "ar",
                "bootcamp_name": row['name_bootcamp'],
                "bootcamp_name_ar": row.get('name_ar_bootcamp', ''),
                "students": row['number_of_students'],
                "start_time": str(row['start_time']),
                "end_time": str(row['end_time']),
                "place_name": row['name_place'],
                "place_name_ar": row.get('name_ar_place', ''),
                "category": row['category'],
                "category_ar": row.get('category_ar', ''),
                "floor": row['floor'],
                "corridor": row['corridor']
            }
        )
        ids.append(f"bootcamp_{i}_ar")
        documents.append(doc_ar)
    
    # Second, add ALL place documents (including those without bootcamps)
    for i, row in places_df.iterrows():
        # 1. English Document
        content_en = generate_place_content(row, "en")
        doc_en = Document(
            page_content=content_en,
            id=f"place_{i}_en",
            metadata={
                "type": "place",
                "lang": "en",
                "place_name": row['name'],
                "place_name_ar": row.get('name_ar', ''),
                "category": row['category'],
                "category_ar": row.get('category_ar', ''),
                "floor": row['floor'],
                "corridor": row['corridor']
            }
        )
        ids.append(f"place_{i}_en")
        documents.append(doc_en)

        # 2. Arabic Document
        content_ar = generate_place_content(row, "ar")
        doc_ar = Document(
            page_content=content_ar,
            id=f"place_{i}_ar",
            metadata={
                "type": "place",
                "lang": "ar",
                "place_name": row['name'],
                "place_name_ar": row.get('name_ar', ''),
                "category": row['category'],
                "category_ar": row.get('category_ar', ''),
                "floor": row['floor'],
                "corridor": row['corridor']
            }
        )
        ids.append(f"place_{i}_ar")
        documents.append(doc_ar)


vector_store = Chroma(
    collection_name='bootcamps',
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_documents:
    vector_store.add_documents(documents=documents, ids=ids)
    

def get_retriever(vector_store, lang: str, k: int = 10):
    """Get language-specific retriever"""
    return vector_store.as_retriever(
        search_kwargs={
            "k": k,
            "filter": {"lang": lang}
        }
    )
