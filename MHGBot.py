from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import getpass
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

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
        self.llm = ChatOpenAI(model="gpt-4o")
        self.embeddings=OpenAIEmbeddings()


        self.vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=self.embeddings)
        self.retriever = self.vectorstore.as_retriever(search_type="similarity")

        self.prompt = ChatPromptTemplate.from_template("""Answer as if you are a friendly helper who is a fellow member of the guild. Answer with as much specific detail as possible. Answer the following question based only on the provided context:

        <context>
        {context}
        </context>

        Question: {input}""")

        document_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.retrieval_chain = create_retrieval_chain(self.retriever, document_chain)

    def scrape_and_store(self):
        loader = WebBaseLoader(["https://sites.google.com/view/mh-guilds/guides-and-stuff/rules-policies", 
                            "https://sites.google.com/view/mh-guilds/welcome",
                            "https://sites.google.com/view/mh-guilds/guides/trading",
                            "https://sites.google.com/view/mh-guilds/guides/healer-stuff",
                            "https://sites.google.com/view/mh-guilds/guides/tank-stuff",
                            "https://sites.google.com/view/mh-guilds/guides/parsing-dps",
                            "https://sites.google.com/view/mh-guilds/raffle"])
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        vectorstore = Chroma.from_documents(documents=splits, embedding=self.embeddings, persist_directory="./chroma_db")
    
    def invoke_llm(self, user_input):
        response = self.retrieval_chain.invoke({"input": user_input})
        return response["answer"]
    
    def update_vectors(self):
        self.vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=self.embeddings)
        self.retriever = self.vectorstore.as_retriever(search_type="similarity")
        document_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.retrieval_chain = create_retrieval_chain(self.retriever, document_chain)
