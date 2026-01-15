"""
Agentic loop (plan/act)
This module will handle the agentic planning and action loop
"""
from dataclasses import dataclass
from .memory import InMemoryStateStore
from .router import RouteDecision
from .answer import AnswerInput , generate_answer


class Agent:
    llm:object
    state_store: InMemoryStateStore
    retriever:object


class RAGAgent:
    def __init__(self , deps:Agent):
        self.deps = deps

    async def handle_turn(self,session_id:str , user_msg: str) -> str:
        state = self.deps.state_store.get_state(session_id)
        
        decision = route_message(user_msg, state)

        state.last_lang = decision.response_lang
        if decision.intent in ["location_lookup", "facility_info"] and decision.place_query:
            state.last_place_query = decision.place_query
        
        # 4) clarify path
        if decision.needs_clarification:
            self.deps.state_store.set(session_id, state)
            return decision.clarification_question or ""

        context = ""
        if decision.intent in ["location_lookup", "facility_info"]:
            context = await self.deps.retriever.retrieve(
                query=decision.place_query or user_msg,
                response_lang=decision.response_lang,
            )

        elif decision.intent == "directions":
            # في الخطوات القادمة: resolve origin/destination + pathfinding
            context = await self.deps.retriever.retrieve(
                query=user_msg,
                response_lang=decision.response_lang,
            )    

        ans = await generate_answer(
            self.deps.llm,
            AnswerInput(
                question=user_msg,
                context=context,
                response_lang = decision.response_lang,
            ),
        )

        self.deps.state_store.set(session_id, state)
        return ans
        

        