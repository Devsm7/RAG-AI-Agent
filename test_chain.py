
import sys
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from vector import retriever

print("🚀 Starting Chain Test...")

# 1. Setup Models (Copied from app.py)
model = ChatOllama(model='llama3.2')

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant. Context: {bootcamps}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

chain = prompt | model

store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

conversation_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history",
)

# 2. Run Test
try:
    message = "Where is cyber security?"
    print(f"❓ Question: {message}")
    
    print("🔍 Invoking Retriever...")
    bootcamps = retriever.invoke(message)
    print(f"✅ Retrieved {len(bootcamps)} docs")
    # print(f"First doc type: {type(bootcamps[0])}")

    print("🤖 Invoking Chain...")
    result = conversation_chain.invoke(
        {"bootcamps": bootcamps, "question": message},
        config={"configurable": {"session_id": "test_session"}}
    )
    print(f"✅ Response: {result.content}")

except Exception as e:
    print(f"❌ Chain Failed: {e}")
    import traceback
    traceback.print_exc()

print("🏁 Test Complete")
