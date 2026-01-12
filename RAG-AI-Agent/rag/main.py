from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from vector import retriever

# Initialize Chat Model
model = ChatOllama(model='llama3.2')

# Define Prompt with History
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant for Twuaiq Academy. Answer the user's question simply and directly using only the provided context. Do NOT repeat the question. Do NOT mention any internal IDs (like place_id or bootcamp_id). If the answer is not in the context, state that you don't know.\n\nImportant: If the context contains time in 24-hour format (e.g., 14:00), YOU MUST convert it to 12-hour format with AM/PM (e.g., 2:00 PM) in your answer.\n\nContext: {bootcamps}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

# Create Chain
chain = prompt | model

# History Management
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Wrap Chain with History
conversation_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history",
)

# Main Loop
if __name__ == "__main__":
    print("Start chatting with the Twuaiq RAG Assistant (type 'q' to quit).")
    session_id = "user_session"

    while True:
        print("---------------------------------------------")
        question = input("Ask your question: ")

        if question.lower() == 'q':
            break
        
        # Retrieve context
        bootcamps = retriever.invoke(question)
        
        # Generate answer with history
        result = conversation_chain.invoke(
            {"bootcamps": bootcamps, "question": question},
            config={"configurable": {"session_id": session_id}}
        )
        
        print(result.content)
