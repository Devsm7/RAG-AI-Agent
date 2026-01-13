## Vector Search is a database; it's gonna be hosted locally in the machine using  ChromaDB , to look up relevant info that we can pass to our model

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd


# Load both CSV files
bootcamps_df = pd.read_csv(r"datasets\bootcamps_db.csv")
places_df = pd.read_csv(r"datasets\places_db.csv")

# Merge bootcamps with places data on place_id
merged_df = bootcamps_df.merge(places_df, left_on='place_id', right_on='id', suffixes=('_bootcamp', '_place'))

# Initialize HuggingFace embeddings (multilingual support for English & Arabic)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    cache_folder="./models"
)

db_location = "./chroma_db"

add_documents = not os.path.exists(db_location)

if add_documents:
    documents = []
    ids = []
    
    # First, add merged bootcamp + place documents
    for i, row in merged_df.iterrows():
        # Create rich content combining bootcamp and place information
        # Create bilingual content (English + Arabic)
        content = (
            f"Bootcamp: {row['name_bootcamp']} | معسكر: {row.get('name_ar_bootcamp', row['name_bootcamp'])}, "
            f"Students: {row['number_of_students']} | الطلاب: {row['number_of_students']}, "
            f"Time: {row['start_time']} to {row['end_time']} | الوقت: من {row['start_time']} إلى {row['end_time']}, "
            f"Location: {row['name_place']} | الموقع: {row.get('name_ar_place', row['name_place'])}, "
            f"Category: {row['category']} | الفئة: {row.get('category_ar', row['category'])}, "
            f"Floor: {row['floor']} | الطابق: {row['floor']}, "
            f"Corridor: {row['corridor']} | الممر: {row['corridor']}"
        )
        
        document = Document(
            page_content=content,
            id=f"bootcamp_{i}",
            metadata={
                "type": "bootcamp",
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

        ids.append(f"bootcamp_{i}")
        documents.append(document)
    
    # Second, add ALL place documents (including those without bootcamps)
    for i, row in places_df.iterrows():
        # Create content for each place
        # Create bilingual content (English + Arabic)
        content = (
            f"Place: {row['name']} | مكان: {row.get('name_ar', row['name'])}, "
            f"Category: {row['category']} | الفئة: {row.get('category_ar', row['category'])}, "
            f"Floor: {row['floor']} | الطابق: {row['floor']}, "
            f"Corridor: {row['corridor']} | الممر: {row['corridor']}"
        )
        
        document = Document(
            page_content=content,
            id=f"place_{i}",
            metadata={
                "type": "place",
                "place_name": row['name'],
                "place_name_ar": row.get('name_ar', ''),
                "category": row['category'],
                "category_ar": row.get('category_ar', ''),
                "floor": row['floor'],
                "corridor": row['corridor']
            }
        )
        
        ids.append(f"place_{i}")
        documents.append(document)

vector_store = Chroma(
    collection_name='bootcamps',
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_documents:
    vector_store.add_documents(documents=documents , ids=ids)

##Connecting LLM & Vector Store
retriever = vector_store.as_retriever(
    search_kwargs={"k":10}
)