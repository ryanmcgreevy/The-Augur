from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryByteStore
import getpass
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
import urllib.request
import requests
from bs4 import BeautifulSoup
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
        self.retriever = self.vectorstore.as_retriever(search_type="mmr", search_kwargs={"lambda_mult":0.5, "k":6})
       
        self.prompt = ChatPromptTemplate.from_template("""Answer as if you are a friendly member of the guild. Answer with as much specific detail as possible, but only if you are confident in the answer. Answer the following question based only on the provided context:

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
                            "https://sites.google.com/view/mh-guilds/guides/healer-role",
                            "https://sites.google.com/view/mh-guilds/guides/tank-role",
                            "https://sites.google.com/view/mh-guilds/guides/dps-role",
                            "https://sites.google.com/view/mh-guilds/raffle",
                            "https://sites.google.com/view/mh-guilds/trial-notes/aetherian-archive"])


        docs = loader.load()

        # url = ("https://drive.google.com/drive/folders/12jfX6Ne1VRS2trAfsO0LPJ4MJZ6wXbbn")
        # page = requests.get(url).text
        # print(page)
        # soup = BeautifulSoup(page, 'html.parser')
        # links = [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith('nc')]
        # for link in links:
        #     print(link)
        #     filename = link.split('/')[-1]
        #     print(filename)
        #     urllib.request.urlretrieve(link,filename)
        #     tloader = TextLoader(filename)
        #     tdoc = tloader.load()
        #     docs.append(tdoc)
        print(os.getcwd())
        #dloader = DirectoryLoader('./MHGBot/mhg', glob="**/*.txt", loader_cls=TextLoader)
        #for tdoc in dloader.load(): docs.append(tdoc)
        dloader = DirectoryLoader('./MHGBot/alcast', glob="**/*.txt", loader_cls=TextLoader)
        for tdoc in dloader.load(): docs.append(tdoc)
        dloader = DirectoryLoader('./MHGBot/skinny_cheeks', glob="**/*.txt", loader_cls=TextLoader)
        for tdoc in dloader.load(): docs.append(tdoc
        dloader = DirectoryLoader('./MHGBot/hacktm', glob="**/*.txt", loader_cls=TextLoader)
        for tdoc in dloader.load(): docs.append(tdoc))
        print(len(docs))
      #  doc_len = 0
      #  for doc in docs: doc_len += len(doc.page_content)
     #   chunk_size = (doc_len/len(docs))/10
      #  chunk_overlap = chunk_size/5
        chunk_size = 1000
        chunk_overlap = 200
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        splits = text_splitter.split_documents(docs)
        self.vectorstore = Chroma.from_documents(documents=splits, embedding=self.embeddings, persist_directory="./chroma_db")
        self.retriever = self.vectorstore.as_retriever(search_type="mmr", search_kwargs={"lambda_mult":0.5, "k":6})
        document_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.retrieval_chain = create_retrieval_chain(self.retriever, document_chain)
    
    def invoke_llm(self, user_input):
        response = self.retrieval_chain.invoke({"input": user_input})
        return response["answer"]

