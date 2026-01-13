from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from vector import retriever
from speech_to_text import SpeechToText

# Initialize Chat Model
model = ChatOllama(model='llama3.2')

# Define Prompt with History (Bilingual Support)
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful bilingual assistant for Twuaiq Academy (أكاديمية طويق). 

Instructions:
- Detect the language of the user's question (English or Arabic)
- Respond in the SAME language as the question
- Answer simply and directly using only the provided context
- Do NOT repeat the question
- Do NOT mention any internal IDs (like place_id or bootcamp_id)
- If the answer is not in the context, state that you don't know

Important:
- If the context contains time in 24-hour format (e.g., 14:00), convert it to 12-hour format with AM/PM (e.g., 2:00 PM) for English or (2:00 مساءً) for Arabic
- The context contains information in both English and Arabic separated by |
- If the context contains the duration of bootcamp in hours , calculate start_time and end_time internally so that don't mention it in answer , only answer DURATION


Context: {bootcamps}"""),
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
    print("=" * 60)
    print("🎓 Twuaiq RAG Assistant with Voice Support")
    print("   مساعد أكاديمية طويق مع دعم الصوت")
    print("=" * 60)
    print("\nCommands / الأوامر:")
    print("  - Type your question in English or Arabic")
    print("    اكتب سؤالك بالإنجليزية أو العربية")
    print("  - Type 'v' to use voice input")
    print("    اكتب 'v' لاستخدام الإدخال الصوتي")
    print("  - Type 'q' to quit")
    print("    اكتب 'q' للخروج")
    print("=" * 60)
    
    session_id = "user_session"
    stt = SpeechToText()  # Initialize speech-to-text

    while True:
        print("\n" + "-" * 60)
        user_input = input("💬 Ask your question (or 'v' for voice, 'q' to quit): ").strip()

        if user_input.lower() == 'q':
            print("\n👋 Goodbye! / وداعاً!")
            break
        
        # Handle voice input
        if user_input.lower() == 'v':
            question = stt.listen_and_transcribe()
            if not question:
                print("❌ No speech detected or transcription failed. Please try again.")
                continue
            print(f"\n📝 You asked: {question}")
        else:
            question = user_input
        
        if not question:
            print("❌ Please ask a question.")
            continue
        
        # Retrieve context
        bootcamps = retriever.invoke(question)
        
        # Generate answer with history
        result = conversation_chain.invoke(
            {"bootcamps": bootcamps, "question": question},
            config={"configurable": {"session_id": session_id}}
        )
        
        print(f"\n🤖 Answer: {result.content}")

