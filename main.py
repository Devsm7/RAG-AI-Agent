from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import PromptTemplate
from vector import retriever

model = OllamaLLM(model='llama3.2')

template = """
You are an expret in answering questions about a twuaiq academy bootcamps

Here are relevant bootcamps: {bootcamps}

Here is the question to answer: {question}
"""

prompt = PromptTemplate.from_template(template)
chain = prompt | model


while True:
    print("---------------------------------------------")
    question = input("Ask your question(q to Quit):")

    if question == 'q':
        break
    
    bootcamps = retriever.invoke(question)
    result = chain.invoke({"bootcamps":bootcamps , "question":question})
    print(result)
