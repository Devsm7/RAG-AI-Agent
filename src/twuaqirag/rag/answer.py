"""
Answer generation wrapper (LLM only)
- No retrieval here
- No chat history here (we use state memory + minimal context)
"""

from dataclasses import dataclass
from typing import Optional

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from twuaqirag.rag.types import ResponseLang
from twuaqirag.rag.prompts import SYSTEM_PROMPT_EN , SYSTEM_PROMPT_AR


_llm = ChatOllama(model="llama3.2")


class AnswerInput:
    question: str
    context:str
    response_lang: ResponseLang 

    style_hint: Optional[str] = None


    def _build_prompt(response_lang: ResponseLang) -> ChatPromptTemplate:
        """
    Build a strict prompt that forces response language and injects context.
    """
        system_template = SYSTEM_PROMPT_AR if response_lang == ResponseLang.ARABIC else SYSTEM_PROMPT_EN

        # Make context explicit and mandatory in the prompt
        # so we never rely on "system prompt contains {bootcamps}" implicitly.
        return ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human",
         "Retrieved Context:\n{context}\n\n"
         "User Question:\n{question}\n\n"
         "Instructions:\n"
         "- Answer in the same language as the system message.\n"
         "- Use only the retrieved context.\n"
         "- If the context is insufficient, ask ONE clarifying question.\n"
        ),
    ])  


    def generate_answer(inp:AnswerInput) -> str:
         """
    Generate answer using LLM based on context & question.
    """

    prompt = _build_prompt(inp.response_lang)
    
    # If you want optional style hint
    context = inp.context
    if inp.style_hint:
        context = f"{context}\n\nStyle hint: {inp.style_hint}"

    chain = prompt | _llm
    result = await chain.ainvoke({
        "question": inp.question,
        "context": context,
    })

    return result.content