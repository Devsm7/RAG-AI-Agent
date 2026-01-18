"""
Answer generation wrapper (LLM only)
- No retrieval here
- No chat history here (we use state memory + retrieved context)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from twuaqirag.core.config import config
from twuaqirag.rag.rag_types import ResponseLang
from twuaqirag.rag.prompts import SYSTEM_PROMPT_EN, SYSTEM_PROMPT_AR


# Initialize language-specific LLM models (important for performance)
_llm_english = ChatOllama(model=config.LLM_MODEL_ENGLISH)
_llm_arabic = ChatOllama(model=config.LLM_MODEL_ARABIC)


def _get_llm(response_lang: ResponseLang) -> ChatOllama:
    """
    Select the appropriate LLM model based on response language.
    
    Args:
        response_lang: The target response language
        
    Returns:
        ChatOllama instance for the specified language
    """
    return _llm_arabic if response_lang == ResponseLang.ARABIC else _llm_english


@dataclass
class AnswerInput:
    question: str
    context: str
    response_lang: ResponseLang
    style_hint: Optional[str] = None


def _build_prompt(response_lang: ResponseLang) -> ChatPromptTemplate:
    """
    Build a strict prompt that forces response language and injects context.
    """
    system_template = (
        SYSTEM_PROMPT_AR if response_lang == ResponseLang.ARABIC else SYSTEM_PROMPT_EN
    )

    return ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            (
                "human",
                "Retrieved Context:\n{context}\n\n"
                "User Question:\n{question}\n\n"
               # "Instructions:\n"
                #"- Answer in the same language as the system message.\n"
                #"- Use only the retrieved context.\n"
                #"- If the context is insufficient, ask ONE clarifying question.\n",
            ),
        ]
    )


async def generate_answer(inp: AnswerInput) -> str:
    """
    Generate answer using language-specific LLM based on context & question.
    """
    prompt = _build_prompt(inp.response_lang)
    llm = _get_llm(inp.response_lang)

    context = inp.context or ""
    if inp.style_hint:
        context = f"{context}\n\nStyle hint: {inp.style_hint}"

    chain = prompt | llm
    result = await chain.ainvoke(
        {
            "question": inp.question,
            "context": context,
        }
    )
    return result.content
