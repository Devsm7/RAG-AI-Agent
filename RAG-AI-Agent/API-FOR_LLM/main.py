from fastapi import FastAPI
from pydantic import BaseModel
import ollama
from rag.vector import retriever

app = FastAPI()

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str

@app.post("/ask", response_model=AskResponse)
def ask_llm(req: AskRequest):
    docs = retriever.invoke(req.question)
    # if  not docs:
    #     return {
    #         "answer": "Iiujiujiujiujszw"
           
    #     }
    
    top_doc = docs[0]
    meta = top_doc.metadata

    prompt = f"""
You are a campus navigation assistant.

Answer ONLY using the context below.
If the answer is not present, say "I don't know".

Context:
{top_doc.page_content}

Question:
{req.question}
"""





    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return {
        "answer":response["message"]["content"],
        "place": meta.get("place_name"),
        "floor": meta.get("floor"),
        "corridor": meta.get("corridor"),
        "category": meta.get("category"),
       
    }
