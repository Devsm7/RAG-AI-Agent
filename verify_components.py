
import sys
import os

# Create datasets and models dirs if not exist, just in case
os.makedirs("datasets", exist_ok=True)
os.makedirs("models", exist_ok=True)

print("🔍 1. Testing Imports...")
try:
    from langchain_ollama import ChatOllama
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_chroma import Chroma
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print("\n🔍 2. Testing Ollama (llama3.2)...")
try:
    model = ChatOllama(model='llama3.2')
    res = model.invoke("Hello, are you working?")
    print(f"✅ Ollama Response: {res.content}")
except Exception as e:
    print(f"❌ Ollama failed: {e}")

print("\n🔍 3. Testing ChromaDB/Retriever...")
try:
    # Minimal mock of vector.py logic without loading full CSVs if possible, 
    # but better to import vector.py if it works
    sys.path.append(os.getcwd())
    from vector import retriever
    
    docs = retriever.invoke("cyber security")
    print(f"✅ Retriever found {len(docs)} documents")
    if len(docs) > 0:
        print(f"   First doc: {docs[0].page_content[:50]}...")
except Exception as e:
    print(f"❌ Retriever failed: {e}")

print("\n🏁 Verification Complete")
