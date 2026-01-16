"""
Agentic loop (route -> retrieve -> answer)
"""
from dataclasses import dataclass

from twuaqirag.rag.memory import InMemoryStateStore
from twuaqirag.rag.router import route_message
from twuaqirag.rag.answer import AnswerInput, generate_answer


@dataclass
class AgentDeps:
    llm: object
    state_store: InMemoryStateStore
    retriever: object  # must implement: async retrieve(query, response_lang) -> str


class RAGAgent:
    def __init__(self, deps: AgentDeps):
        self.deps = deps

    async def handle_turn(self, session_id: str, user_msg: str) -> str:
        # 1) Load state
        state = self.deps.state_store.get(session_id)

        # 2) Route (language + intent + entities)
        decision = route_message(user_msg, state)

        # 3) Update state (minimal, no translating history)
        state.last_lang = decision.response_lang
        if decision.intent in ["location_lookup", "facility_info"] and decision.place_query:
            state.last_place_query = decision.place_query

        # 4) Clarify if needed
        if decision.needs_clarification:
            self.deps.state_store.set(session_id, state)
            return decision.clarification_question or ""

        # 5) Retrieve context
        if decision.intent in ["location_lookup", "facility_info"]:
            query = decision.place_query or user_msg
        else:
            query = user_msg  # directions/general for now

        context = await self.deps.retriever.retrieve(
            query=query,
            response_lang=decision.response_lang,
        )

        # 6) Generate answer (enforce response language via prompts)
        # Important: generate_answer already uses internal singleton llm OR uses deps.llm depending on your answer.py design
        # If your generate_answer uses internal _llm, you can remove deps.llm entirely.
        answer = await generate_answer(
            AnswerInput(
                question=user_msg,
                context=context,
                response_lang=decision.response_lang,
            )
        )

        # 7) Persist state
        self.deps.state_store.set(session_id, state)
        return answer
