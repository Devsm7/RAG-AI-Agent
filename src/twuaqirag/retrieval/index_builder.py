"""
Build/update vector index from CSV files
Creates bilingual documents for bootcamps and places
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from twuaqirag.core.config import config


def load_places_from_csv(csv_path: Path) -> List[Document]:
    """
    Load places from CSV and create bilingual documents.
    
    Each place gets two documents: one in English, one in Arabic.
    """
    documents = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            place_id = row['id']
            name = row['name']
            name_ar = row.get('name_ar', name)  # Use Arabic name from CSV
            category = row['category']
            category_ar = row.get('category_ar', category)  # Use Arabic category from CSV
            floor = row['floor']
            corridor = row.get('corridor', '')
            
            # Create English document
            en_content = f"""Place: {name}
Category: {category}
Floor: {floor}
Corridor: {corridor if corridor and corridor != 'NULL' else 'N/A'}
Location: Floor {floor}, Corridor {corridor if corridor and corridor != 'NULL' else 'Main Area'}

This is {name}, a {category} located on floor {floor}."""
            
            en_doc = Document(
                page_content=en_content,
                metadata={
                    'place_id': place_id,
                    'name': name,
                    'category': category,
                    'floor': floor,
                    'corridor': corridor if corridor != 'NULL' else '',
                    'lang': 'en',
                    'type': 'place'
                }
            )
            documents.append(en_doc)
            
            # Create Arabic document using CSV data
            ar_content = f"""المكان: {name_ar}
الفئة: {category_ar}
الطابق: {floor}
الممر: {corridor if corridor and corridor != 'NULL' else 'غير محدد'}
الموقع: الطابق {floor}، الممر {corridor if corridor and corridor != 'NULL' else 'المنطقة الرئيسية'}

هذا هو {name_ar}، وهو {category_ar} يقع في الطابق {floor}."""
            
            ar_doc = Document(
                page_content=ar_content,
                metadata={
                    'place_id': place_id,
                    'name': name,
                    'name_ar': name_ar,
                    'category': category,
                    'category_ar': category_ar,
                    'floor': floor,
                    'corridor': corridor if corridor != 'NULL' else '',
                    'lang': 'ar',
                    'type': 'place'
                }
            )
            documents.append(ar_doc)
    
    return documents


def load_bootcamps_from_csv(csv_path: Path, places_csv_path: Path) -> List[Document]:
    """
    Load bootcamps from CSV and create bilingual documents.
    
    Links bootcamps to their places and includes schedule information.
    """
    # First, load places to create a lookup map
    places_map = {}
    with open(places_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            places_map[row['id']] = {
                'name': row['name'],
                'floor': row['floor'],
                'corridor': row.get('corridor', '')
            }
    
    documents = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bootcamp_id = row['id']
            name = row['name']
            name_ar = row.get('name_ar', name)  # Use Arabic name from CSV
            num_students = row['number_of_students']
            start_time = row['start_time']
            end_time = row['end_time']
            place_id = row['place_id']
            
            # Get place information
            place_info = places_map.get(place_id, {})
            place_name = place_info.get('name', 'Unknown')
            floor = place_info.get('floor', 'Unknown')
            corridor = place_info.get('corridor', '')
            
            # Convert 24-hour time to 12-hour format
            def format_time_12hr(time_24):
                """Convert 24:00:00 to 12-hour format"""
                hour, minute, _ = time_24.split(':')
                hour = int(hour)
                period = 'PM' if hour >= 12 else 'AM'
                if hour > 12:
                    hour -= 12
                elif hour == 0:
                    hour = 12
                return f"{hour}:{minute} {period}"
            
            start_12hr = format_time_12hr(start_time)
            end_12hr = format_time_12hr(end_time)
            
            # Create English document
            en_content = f"""Bootcamp: {name}
Number of Students: {num_students}
Schedule: {start_12hr} to {end_12hr} (Daily)
Location: {place_name}, Floor {floor}{f', Corridor {corridor}' if corridor and corridor != 'NULL' else ''}

The {name} bootcamp is held in {place_name} on floor {floor}. 
Classes run from {start_12hr} to {end_12hr} daily.
Currently, there are {num_students} students enrolled in this program."""
            
            en_doc = Document(
                page_content=en_content,
                metadata={
                    'bootcamp_id': bootcamp_id,
                    'name': name,
                    'place_id': place_id,
                    'place_name': place_name,
                    'floor': floor,
                    'corridor': corridor if corridor != 'NULL' else '',
                    'start_time': start_time,
                    'end_time': end_time,
                    'num_students': num_students,
                    'lang': 'en',
                    'type': 'bootcamp'
                }
            )
            documents.append(en_doc)
            
            # Create Arabic document using CSV data
            ar_content = f"""المعسكر: {name_ar}
عدد الطلاب: {num_students}
الجدول الزمني: من {start_12hr} إلى {end_12hr} (يومياً)
الموقع: {place_name}، الطابق {floor}{f'، الممر {corridor}' if corridor and corridor != 'NULL' else ''}

يُعقد معسكر {name_ar} في {place_name} في الطابق {floor}.
تبدأ الحصص من {start_12hr} إلى {end_12hr} يومياً.
حالياً، هناك {num_students} طالب مسجلين في هذا البرنامج."""
            
            ar_doc = Document(
                page_content=ar_content,
                metadata={
                    'bootcamp_id': bootcamp_id,
                    'name': name,
                    'name_ar': name_ar,
                    'place_id': place_id,
                    'place_name': place_name,
                    'floor': floor,
                    'corridor': corridor if corridor != 'NULL' else '',
                    'start_time': start_time,
                    'end_time': end_time,
                    'num_students': num_students,
                    'lang': 'ar',
                    'type': 'bootcamp'
                }
            )
            documents.append(ar_doc)
    
    return documents


def build_index():
    """
    Main function to build the vector index from CSV files.
    """
    print("🔨 Building vector index from CSV files...")
    
    # Define paths
    bootcamps_csv = config.PROJECT_ROOT / "datasets" / "bootcamps_new.csv"
    places_csv = config.PROJECT_ROOT / "datasets" / "places_new.csv"
    chroma_dir = config.CHROMA_DB_DIR
    
    # Verify files exist
    if not bootcamps_csv.exists():
        raise FileNotFoundError(f"Bootcamps CSV not found: {bootcamps_csv}")
    if not places_csv.exists():
        raise FileNotFoundError(f"Places CSV not found: {places_csv}")
    
    print(f"📂 Loading data from:")
    print(f"   - {bootcamps_csv}")
    print(f"   - {places_csv}")
    
    # Load documents
    print("📄 Loading places...")
    places_docs = load_places_from_csv(places_csv)
    print(f"   ✅ Created {len(places_docs)} place documents ({len(places_docs)//2} places × 2 languages)")
    
    print("📄 Loading bootcamps...")
    bootcamp_docs = load_bootcamps_from_csv(bootcamps_csv, places_csv)
    print(f"   ✅ Created {len(bootcamp_docs)} bootcamp documents ({len(bootcamp_docs)//2} bootcamps × 2 languages)")
    
    # Combine all documents
    all_docs = places_docs + bootcamp_docs
    print(f"\n📊 Total documents: {len(all_docs)}")
    
    # Initialize embeddings
    print("\n🔄 Initializing embedding model (mxbai-embed-large)...")
    embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL)
    
    # Create/update vector store
    print(f"💾 Creating vector store in: {chroma_dir}")
    vector_store = Chroma.from_documents(
        documents=all_docs,
        embedding=embeddings,
        collection_name="twuiqiraq",
        persist_directory=str(chroma_dir)
    )
    
    print(f"\n✅ Index built successfully!")
    print(f"   - Total documents indexed: {len(all_docs)}")
    print(f"   - Places: {len(places_docs)//2} ({len(places_docs)} docs)")
    print(f"   - Bootcamps: {len(bootcamp_docs)//2} ({len(bootcamp_docs)} docs)")
    print(f"   - Storage location: {chroma_dir}")
    
    # Test query
    print("\n🔍 Testing retrieval...")
    results = vector_store.similarity_search("Unity", k=2)
    if results:
        print(f"   ✅ Test query successful! Found {len(results)} results")
        print(f"   Sample: {results[0].page_content[:100]}...")
    else:
        print("   ⚠️  No results found in test query")
    
    return vector_store


if __name__ == "__main__":
    try:
        build_index()
        print("\n🎉 Index building completed successfully!")
    except Exception as e:
        print(f"\n❌ Error building index: {e}")
        raise
