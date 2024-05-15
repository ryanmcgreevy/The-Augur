from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import getpass
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

class MHGBot:
    
    def __init__(self) -> None:
        
        #for offline llm
        #from langchain_community.llms import Ollama
        #from langchain_community.embeddings import OllamaEmbeddings
        #for offline llm
        #llm = Ollama(model="llama3")
        #embeddings = OllamaEmbeddings()

        #Uncomment if you want to pass the API key every time. You can also set it directly here.
        #For now, we are using the environment variable set by our bash profile
        #os.environ["OPENAI_API_KEY"] = getpass.getpass()

        #llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
        llm = ChatOpenAI(model="gpt-4o")
        embeddings=OpenAIEmbeddings()


        vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
        retriever = vectorstore.as_retriever(search_type="similarity")

        prompt = ChatPromptTemplate.from_template("""Answer as if you are a friendly helper who is a fellow member of the guild. Answer with as much specific detail as possible. Answer the following question based only on the provided context:

        <context>
        {context}
        </context>

        Question: {input}""")

        document_chain = create_stuff_documents_chain(llm, prompt)
        self.retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    def invoke_llm(self, user_input):
        response = self.retrieval_chain.invoke({"input": user_input})
        return response["answer"]
