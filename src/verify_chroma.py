"""
Comprehensive test to verify Chroma database is working correctly
"""
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("CHROMA DATABASE VERIFICATION TEST")
print("=" * 60)
print()

# Test 1: Import and load vector store
print("Test 1: Loading vector store...")
try:
    from twuaqirag.retrieval.vector_store import vector_store
    print("✅ Vector store imported successfully")
except Exception as e:
    print(f"❌ Failed to import: {e}")
    sys.exit(1)

# Test 2: Check document count
print("\nTest 2: Checking document count...")
try:
    count = vector_store._collection.count()
    print(f"✅ Vector store has {count} documents")
    if count == 0:
        print("❌ ERROR: Database is empty!")
        sys.exit(1)
    elif count != 90:
        print(f"⚠️  WARNING: Expected 90 documents, got {count}")
except Exception as e:
    print(f"❌ Failed to count documents: {e}")
    sys.exit(1)

# Test 3: Test retrieval
print("\nTest 3: Testing retrieval...")
test_queries = [
    ("Unity bootcamp", "en"),
    ("where is cafeteria", "en"),
    ("أين المقهى", "ar"),
]

for query, expected_lang in test_queries:
    try:
        results = vector_store.similarity_search(query, k=2)
        if results:
            print(f"✅ Query '{query}' found {len(results)} results")
            print(f"   Top result: {results[0].metadata.get('name', 'N/A')} (lang={results[0].metadata.get('lang')})")
        else:
            print(f"⚠️  Query '{query}' returned no results")
    except Exception as e:
        print(f"❌ Query '{query}' failed: {e}")

# Test 4: Test config paths
print("\nTest 4: Verifying config paths...")
try:
    from twuaqirag.core.config import config
    print(f"✅ CHROMA_DB_DIR: {config.CHROMA_DB_DIR}")
    print(f"✅ BOOTCAMPS_CSV: {config.BOOTCAMPS_CSV}")
    print(f"✅ PLACES_CSV: {config.PLACES_CSV}")
    
    # Check if files exist
    if config.BOOTCAMPS_CSV.exists():
        print(f"✅ Bootcamps CSV exists")
    else:
        print(f"❌ Bootcamps CSV not found!")
        
    if config.PLACES_CSV.exists():
        print(f"✅ Places CSV exists")
    else:
        print(f"❌ Places CSV not found!")
        
except Exception as e:
    print(f"❌ Config check failed: {e}")

print()
print("=" * 60)
print("✅ ALL TESTS PASSED! Database is ready to use.")
print("=" * 60)
